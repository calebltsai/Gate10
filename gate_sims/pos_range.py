import os
import opengate as gate
import uproot
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from opengate.actors.filters import GateFilterBuilder

def run_annihilation_simulation():
    print("=== Phase 1: Running GATE 10 Simulation ===")
    
    # Initialize Simulation
    sim = gate.Simulation()
    sim.output_dir = "./out"
    sim.number_of_threads = 1
    sim.run_timing_intervals = [[0.0, 10*gate.g4_units.second]]

    # Shortcuts for units
    cm = gate.g4_units.cm
    MeV = gate.g4_units.MeV
    Bq = gate.g4_units.Bq

    # Geometry
    world = sim.world
    world.size = [5 * cm, 5 * cm, 5 * cm]
    
    Annihilation_box = sim.add_volume("Box", "Annihilation_Box")
    Annihilation_box.size = [2 * cm, 2 * cm, 2 * cm]
    Annihilation_box.material = "G4_ADIPOSE_TISSUE_ICRP"
    Annihilation_box.color = [0, 0, 1, 1]  # Blue

    # Physics Configuration
    sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"

    # Positron Source
    source = sim.add_source("GenericSource", "PositronSource")
    source.particle = "e+"
    source.position.type = "point"
    source.activity = 100000*Bq
    source.energy.type = "mono"
    source.energy.mono = 1 * MeV

    # Actor Configuration
    ps_actor = sim.add_actor("PhaseSpaceActor", "AnnihilationTracker")
    ps_actor.attached_to = "world"
    ps_actor.output_filename = "annihilation_data.root"
    
    # GATE 10 standard naming attributes for PhaseSpace
    ps_actor.attributes = [
        "KineticEnergy",
        "ParticleName"
    ]
    ps_actor.steps_to_store = "all"

    f_creation = GateFilterBuilder()
    
    # Filter: Capture gammas created explicitly by the 'annihil' process
    annihilation_filter = (f_creation.ParticleName == "gamma") & (f_creation.KineticEnergy >= 0.510*MeV)
    
    # Apply the logical filter expression directly to your PhaseSpaceActor
    ps_actor.filter = annihilation_filter

    # Execute simulation
    sim.run()
    print("=== Simulation Complete! ===\n")
    return ps_actor.get_output_path()


def analyze_and_export_to_csv(path):
    print("=== Phase 2: Converting ROOT Trees to CSV Data Sheet ===")
    root_file_path = path
    
    if not os.path.exists(root_file_path):
        raise FileNotFoundError(f"Expected ROOT file not found at: {root_file_path}")

    # Open the compiled ROOT file tree
    file = uproot.open(root_file_path)
    tree = file["AnnihilationTracker"]

    # Pull out your customized tracking attributes into a DataFrame
    df = tree.arrays(["KineticEnergy", "ParticleName"], library="pd")

    # Filter to strictly isolate gamma rays created by positron annihilation in water
    annihilation_data = df[(df["ParticleName"] == "gamma")]

    # Drop the string filtering columns to keep the file size minimal for MATLAB
    # This leaves you with a clean array/vector of your target kinetic energies
    csv_ready_data = annihilation_data[["KineticEnergy"]]

    if len(csv_ready_data) == 0:
        print("Warning: Zero filtered annihilation tracks found. Nothing written.")
        return

    # Export to a standard CSV file (index=False prevents extra index column injection)
    output_csv_path = "./out/adipose_tissue_ICRP_annihilation_energies.csv"
    csv_ready_data.to_csv(output_csv_path, index=False)
    
    print(f"Success! {len(csv_ready_data)} events saved successfully to layout matrix.")
    print(f"File destination: {output_csv_path}")

if __name__ == "__main__":
    # Execute the entire automated workflow
    filepath = run_annihilation_simulation()
    analyze_and_export_to_csv(filepath)