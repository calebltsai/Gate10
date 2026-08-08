import os
import opengate as gate
import uproot
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from opengate.actors.filters import GateFilterBuilder
from opengate.geometry import fields

def run_edep_simulation():
    print("=== Phase 1: Running GATE 10 Simulation ===")
    
    # Initialize Simulation
    sim = gate.Simulation()
    sim.output_dir = "./out"
    sim.number_of_threads = 4
    sim.random_seed = "auto"
    sim.run_timing_intervals = [[0.0, 1*gate.g4_units.second]]

    # Shortcuts for units
    cm = gate.g4_units.cm
    MeV = gate.g4_units.MeV
    Bq = gate.g4_units.Bq

    # Geometry
    world = sim.world
    world.size = [2.4 * cm, 2.4 * cm, 2.4 * cm]
    
    phantom_box = sim.add_volume("Box", "Phantom_Box")
    phantom_box.size = [2 * cm, 2 * cm, 2 * cm]
    phantom_box.material = "G4_WATER"
    phantom_box.color = [0, 0, 1, 1]  # Blue

    # Physics Configuration
    sim.physics_manager.enable_decay = True
    sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"
    # sim.physics_manager.set_track_structure_em_physics(
    #     volume_name='Phantom_Box', 
    #     track_structure_em_physics='G4EmDNAPhysics_option4'
    # )
    sim.physics_manager.user_limits_particles = ['electron', 'positron', 'gamma']
    sim.physics_manager.set_production_cut("Phantom_Box", "gamma", 0.01 * cm)
    sim.physics_manager.set_production_cut("Phantom_Box", "electron", 0.005 * cm)
    sim.physics_manager.set_production_cut("Phantom_Box", "positron", 0.005 * cm)
    sim.physics_manager.set_max_step_size("Phantom_Box", 0.01 * cm)

    # Positron Source
    source = sim.add_source("GenericSource", "Ga68Source")
    source.particle = 'ion 31 68'  # Gallium68
    source.position.type = "point"
    source.activity = 50000*Bq
    source.direction.type = "iso"

    field = fields.UniformMagneticField(name="B_field_for_box")
    field.field_vector = [0, 0, 9.0 * gate.g4_units.tesla]
    field.stepper = "DormandPrince745"  # Or "HelixSimpleRunge"
    field.delta_chord = 0.005 * cm
    phantom_box.add_field(field)

    # Actor Configuration
    ps_actor = sim.add_actor("PhaseSpaceActor", "FullTracker")
    ps_actor.attached_to = "world"
    ps_actor.output_filename = "Ga68_9T.root"
    
    # GATE 10 standard naming attributes for PhaseSpace
    ps_actor.attributes = [
        "ParticleName",
        "KineticEnergy",
        "TotalEnergyDeposit",
        "ProcessDefinedStep",
        "PostPosition",
        "EventID",
        "EventPosition",
        "ParentID"
    ]

    ps_actor.steps_to_store = "all"

    # Execute simulation
    sim.run()
    print("=== Simulation Complete! ===\n")
    return ps_actor.get_output_path()


# def analyze_and_export_to_csv(path):
#     print("=== Phase 2: Converting ROOT Trees to CSV Data Sheet ===")
#     root_file_path = path
    
#     if not os.path.exists(root_file_path):
#         raise FileNotFoundError(f"Expected ROOT file not found at: {root_file_path}")

#     # Open the compiled ROOT file tree
#     file = uproot.open(root_file_path)
#     tree = file["EdepTracker"]

#     # Pull out your customized tracking attributes into a DataFrame
#     df = tree.arrays(["ParticleName", "KineticEnergy", "PostPosition_X", "PostPosition_Y", "PostPosition_Z", "TotalEnergyDeposit", "ProcessDefinedStep", "EventID", "EventPosition_X", "EventPosition_Y", "EventPosition_Z"], library="pd")
#     # Filter to strictly isolate positron in water
#     edep_data = df
#     # Drop the string filtering columns to keep the file size minimal for MATLAB
#     # This leaves you with a clean table of your relevant data
#     csv_ready_data = edep_data[["ParticleName", "KineticEnergy", "TotalEnergyDeposit", "ProcessDefinedStep", "EventID", "PostPosition_X", "PostPosition_Y", "PostPosition_Z","EventPosition_X", "EventPosition_Y", "EventPosition_Z" ]]

#     if len(csv_ready_data) == 0:
#         print("Warning: Zero edep actions found. Nothing written.")
#         return

#     # Export to a standard CSV file (index=False prevents extra index column injection)
#     output_csv_path = "./out/F18/F18_full.csv"
#     csv_ready_data.to_csv(output_csv_path, index=False)
    
#     print(f"Success! {len(csv_ready_data)} events saved successfully to layout matrix.")
#     print(f"File destination: {output_csv_path}")

if __name__ == "__main__":
    # Execute the entire automated workflow
    filepath = run_edep_simulation()
    # analyze_and_export_to_csv(filepath)