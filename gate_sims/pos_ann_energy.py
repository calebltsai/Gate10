import opengate as gate

# Initialize the master simulation object
sim = gate.Simulation()
sim.g4_verbose = False
sim.visu = False
sim.random_seed = 'auto'
sim.number_of_threads = 4

# -------------------------------------------------------------
# 1. GEOMETRY & MATERIALS
# -------------------------------------------------------------
# World Volume
cm = gate.g4_units.cm
eV = gate.g4_units.eV
MeV = gate.g4_units.MeV

world = sim.world
world.size = [400, 400, 400]  # mm
world.material = "G4_AIR"

# Penetrating Volume Box (Water block for PALS)
specimen = sim.add_volume("Box", "pen_vol")
specimen.material = "Water"
specimen.size = [20, 20, 5]  # mm
specimen.translation = [0, 0, 3]  # mm

# -------------------------------------------------------------
# 2. PHYSICS DEFINITION
# -------------------------------------------------------------
# Standard high-precision EM physics for low-energy positrons
sim.physics_manager.physics_list_name = "G4EmStandardPhysics_option4"
sim.physics_manager.cuts["world"] = {"e+": 0.1, "e-": 0.1, "gamma": 0.1}  # mm
sim.physics_manager.cuts["specimen_block"] = {"e+": 0.01, "e-": 0.01, "gamma": 0.01}

# -------------------------------------------------------------
# 3. Na-22 ISOTOPE SOURCE (Ion Source)
# -------------------------------------------------------------
source = sim.add_source("Generic", "na22_source")
source.particle = "ion"
# Ion configuration: Z=11 (Na), A=22
source.ion = [11, 22, 0, 0]
source.activity = 50000  # Bq
source.position.type = "cylinder"
source.position.radius = 1.0  # mm
source.position.halfz = 0.01  # mm

# -------------------------------------------------------------
# 4. TRACKING DATA OUTPUT (Phase Space)
# -------------------------------------------------------------
# This tracks exact times and locations inside your sample
ps = sim.add_actor("PhaseSpaceActor", "pals_tracker")
ps.mother = "specimen_block"
ps.output = "out/pals_output.root"
ps.attributes = ["KineticEnergy", "Time", "ProductionVolume", "ParticleName"]

# -------------------------------------------------------------
# 5. RUN EXECUTION
# -------------------------------------------------------------
# Set runtime to sample 100,000 decay opportunities
sim.run_timing_intervals = [[0, 10]]  # seconds
sim.run()