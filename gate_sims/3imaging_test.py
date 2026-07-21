#!/usr/bin/env python3
import opengate as gate
import numpy as np
import uproot
import pandas as pd
import opengate.contrib.pet.siemensbiograph as pet_biograph

def main():
    # 1. Initialize Simulation Manager
    sim = gate.Simulation()
    sim.set_g4_verbose(False)
    sim.set_g4_visualisation(False) # Turn True if you want a Geant4 UI window
    
    # 2. Scanner Geometry (Approximate Siemens Biograph 600)
    pet = pet_biograph.add_pet(sim, "my_pet")
    singles = pet_biograph.add_digitizer(sim, pet.name, "singles.root", hits_name="Hits", singles_name="Singles") 

    # 3. Physics Configuration
    # Use standard high-precision standard electromagnetic list (emstandard_opt4)
    # essential for tracking precise photon interactions and Compton edge resolutions.
    sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"
    
    # 4. Ortho-Positronium Source (3 Gamma Channel)
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
