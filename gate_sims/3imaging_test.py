#!/usr/bin/env python3
import opengate as gate
import numpy as np
import uproot
import pandas as pd

def main():
    # -------------------------------------------------------------------------
    # 1. Initialize Simulation Manager
    # -------------------------------------------------------------------------
    sim = gate.Simulation()
    sim.set_g4_verbose(False)
    sim.set_g4_visualisation(False) # Turn True if you want a Geant4 UI window
    
    # -------------------------------------------------------------------------
    # 2. Scanner Geometry (Approximate Siemens Biograph 600)
    # -------------------------------------------------------------------------
    # The World volume is automatically instantiated as Air by GATE 10
    world = sim.volume_manager.get_world_volume()
    
    # Define a generic cylindrical PET setup 
    # Siemens Biograph: Inner ring radius ~421mm, Axial length ~162mm
    biograph_ring = sim.add_volume("Cylinder", "pet_ring")
    biograph_ring.parent = world.name
    biograph_ring.material = "Lead" # Shielding outer wall casing
    biograph_ring.rmin = 420.0 * gate.mm
    biograph_ring.rmax = 450.0 * gate.mm
    biograph_ring.size_z = 162.0 * gate.mm
    biograph_ring.color = [0.5, 0.5, 0.5, 1.0] # Gray representation
    
    # Add LSO Crystal Ring inside the cylinder casing
    crystal_layer = sim.add_volume("Cylinder", "lso_crystals")
    crystal_layer.parent = biograph_ring.name
    crystal_layer.material = "LSO" # Lutetium Oxyorthosilicate scintillator
    crystal_layer.rmin = 421.0 * gate.mm
    crystal_layer.rmax = 441.0 * gate.mm # 20mm crystal thickness
    crystal_layer.size_z = 162.0 * gate.mm
    crystal_layer.color = [0.0, 0.8, 0.8, 0.6] # Cyan transparent 
    
    # -------------------------------------------------------------------------
    # 3. Physics Configuration
    # -------------------------------------------------------------------------
    # Use standard high-precision standard electromagnetic list (emstandard_opt4)
    # essential for tracking precise photon interactions and Compton edge resolutions.
    sim.physics_manager.set_physics_list("G4EmStandardPhysics_option4")
    
    # Set electron/photon production cuts inside the tracking medium
    sim.physics_manager.set_production_cut("lso_crystals", "gamma", 1.0 * gate.mm)
    sim.physics_manager.set_production_cut("lso_crystals", "e-", 1.0 * gate.mm)
    
    # -------------------------------------------------------------------------
    # 4. Ortho-Positronium Source (3 Gamma Channel)
    # -------------------------------------------------------------------------
    # Instead of simulating standard isotope e+ decays that yield back-to-back pairs, 
    # we initialize a primary particle source tracking specifically the 3-gamma o-Ps decay continuum
    source = sim.add_source("GenericSource", "ops_source")
    source.particle = "gamma"
    source.activity = 50000 * gate.Bq # 50 kHz simulation event execution threshold
    
    # Spatial profile: Small centered distribution block inside a phantom container
    source.position.type = "Sphere"
    source.position.radius = 2.0 * gate.mm
    source.position.translation = [0, 0, 0]
    
    # Kinematic profile: Map to the 3-gamma continuous energy phase space (Ore-Powell)
    # GATE 10 uses a dedicated macro-helper binding configuration for Positronium states
    source.energy.type = "Positronium3G" 
    source.direction.type = "PositroniumCoplanar" 
    
    # -------------------------------------------------------------------------
    # 5. Digitizer & Output Actors
    # -------------------------------------------------------------------------
    # Attach a Hit Actor to map interactions inside the LSO volumes
    hit_actor = sim.add_actor("DigitizerHitsActor", "hits_recorder")
    hit_actor.mother = "lso_crystals"
    hit_actor.output = "biograph_output_hits.root" # Generates data in root canvas
    
    # Configure the basic energy resolution characteristics of LSO (12% FWHM at 511)
    hit_actor.energy_resolution = 0.12
    hit_actor.energy_reference = 511.0 * gate.keV
    hit_actor.low_energy_threshold = 200.0 * gate.keV # Ignore low background scatter
    
    # -------------------------------------------------------------------------
    # 6. Execute Simulation Run
    # -------------------------------------------------------------------------
    # Set execution time bounds
    sim.run_timing.start_time = 0.0 * gate.s
    sim.run_timing.end_time = 1.0 * gate.s # 1 second simulation scale
    
    print("Initializing GATE 10 - Geant4 Context Layer...")
    sim.start()
    print("Simulation finished. Data saved to biograph_output_hits.root")

def parse_coincidence_data():
    # Open the ROOT file constructed by GATE 10
    file = uproot.open("biograph_output_hits.root")
    hits_tree = file["hits_recorder"]

    # Convert tree data fields directly into a DataFrame
    df = hits_tree.arrays(["eventID", "edep", "posX", "posY", "posZ"], library="pd")

    # Filter out rows to keep only true triple coincidence instances (events with exactly 3 hits)
    triple_coincidences = df.groupby("eventID").filter(lambda x: len(x) == 3)

    print(triple_coincidences.head())

if __name__ == "__main__":
    # GATE 10 requires explicitly guarding execution scripts under the __main__ hook 
    # to safely scale multithreaded worker loops.
    main()
