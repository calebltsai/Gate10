import os
import opengate as gate
import uproot
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from opengate.actors.filters import GateFilterBuilder

initenergy = np.linspace(0.1,1,2)

def run_edep_simulation(sourceenergy):
    print("=== Phase 1: Running GATE 10 Simulation ===")
    
    # Initialize Simulation
    sim = gate.Simulation()
    sim.output_dir = "./out"
    sim.number_of_threads = 1
    sim.random_seed = "auto"
    sim.run_timing_intervals = [[0.0, 5*gate.g4_units.second]]

    # Shortcuts for units
    cm = gate.g4_units.cm
    MeV = gate.g4_units.MeV
    Bq = gate.g4_units.Bq

    # Geometry
    world = sim.world
    world.size = [4 * cm, 4 * cm, 4 * cm]
    
    phantom_box = sim.add_volume("Box", "Phantom_Box")
    phantom_box.size = [2 * cm, 2 * cm, 2 * cm]
    phantom_box.material = "G4_WATER"
    phantom_box.color = [0, 0, 1, 1]  # Blue

    # Physics Configuration
    sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"

    # Positron Source
    source = sim.add_source("GenericSource", "PositronSource")
    source.particle = "e-"
    source.position.type = "point"
    source.activity = 100000*Bq
    source.energy.type = "mono"
    source.direction.type = "iso"
    source.energy.mono = sourceenergy * MeV

    # Actor Configuration
    ps_actor = sim.add_actor("PhaseSpaceActor", "edepTracker")
    ps_actor.attached_to = "Phantom_Box"
    ps_actor.output_filename = "edep.root"
    
    # GATE 10 standard naming attributes for PhaseSpace
    ps_actor.attributes = [
        "ParticleName",
        "KineticEnergy",
        "TotalEnergyDeposit",
        "ProcessDefinedStep",
        "TrackID"
    ]
    ps_actor.steps_to_store = "all"

    f_action = GateFilterBuilder()
    
    # Filter: Capture edep energy and process
    edep_filter = (f_action.ParticleName == "e-") & (f_action.TrackID == 1)
    
    # Apply the logical filter expression directly to your PhaseSpaceActor
    ps_actor.filter = edep_filter

    # Execute simulation
    sim.run(start_new_process=True)
    print("=== Simulation Complete! ===\n")
    return ps_actor.get_output_path()


def analyze_and_export_to_csv(path, sourceenergy):
    print("=== Phase 2: Converting ROOT Trees to CSV Data Sheet ===")
    root_file_path = path
    
    if not os.path.exists(root_file_path):
        raise FileNotFoundError(f"Expected ROOT file not found at: {root_file_path}")

    # Open the compiled ROOT file tree
    file = uproot.open(root_file_path)
    print("past_uproot")
    tree = file["edepTracker"]

    # Pull out your customized tracking attributes into a DataFrame
    df = tree.arrays(["TotalEnergyDeposit", "ParticleName", "ProcessDefinedStep", "TrackID"], library="pd")
    print("past_df_creation")
    # Filter to strictly isolate positron in water
    edep_data = df[(df["ParticleName"] == "e-") & (df["TrackID"] == 1)]
    print("past_df_filter")
    # Drop the string filtering columns to keep the file size minimal for MATLAB
    # This leaves you with a clean table of your relevant data
    csv_ready_data = edep_data[["ParticleName", "TotalEnergyDeposit", "ProcessDefinedStep"]]

    if len(csv_ready_data) == 0:
        print("Warning: Zero edep actions found. Nothing written.")
        return

    # Export to a standard CSV file (index=False prevents extra index column injection)
    output_csv_path = "./out/"+str(sourceenergy)+"MeV_el_water_edep.csv"
    csv_ready_data.to_csv(output_csv_path, index=False)
    
    print(f"Success! {len(csv_ready_data)} events saved successfully to layout matrix.")
    print(f"File destination: {output_csv_path}")

if __name__ == "__main__":
    # Execute the entire automated workflow
    for en in initenergy:
        filepath = run_edep_simulation(en)
        analyze_and_export_to_csv(filepath, en)