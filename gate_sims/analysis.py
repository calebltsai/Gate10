import os
import opengate as gate
import uproot
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from opengate.actors.filters import GateFilterBuilder

def analyze_and_export_to_csv(path):
    print("=== Phase 2: Converting ROOT Trees to CSV Data Sheet ===")
    root_file_path = path
    
    if not os.path.exists(root_file_path):
        raise FileNotFoundError(f"Expected ROOT file not found at: {root_file_path}")

    # Open the compiled ROOT file tree
    file = uproot.open(root_file_path)
    tree = file["EdepTracker"]

    # Pull out your customized tracking attributes into a DataFrame
    df = tree.arrays(["ParticleName", "PostPosition_X", "PostPosition_Y", "PostPosition_Z", "TotalEnergyDeposit", "ProcessDefinedStep", "EventID"], library="pd")
    # Filter to strictly isolate positron in water
    edep_data = df
    # Drop the string filtering columns to keep the file size minimal for MATLAB
    # This leaves you with a clean table of your relevant data
    csv_ready_data = edep_data[["ParticleName", "TotalEnergyDeposit", "ProcessDefinedStep", "PostPosition_X", "PostPosition_Y", "PostPosition_Z", "EventID"]]

    if len(csv_ready_data) == 0:
        print("Warning: Zero edep actions found. Nothing written.")
        return

    # Export to a standard CSV file (index=False prevents extra index column injection)
    output_csv_path = "./out/F18/F18_full.csv"
    csv_ready_data.to_csv(output_csv_path, index=False)
    
    print(f"Success! {len(csv_ready_data)} events saved successfully to layout matrix.")
    print(f"File destination: {output_csv_path}")

if __name__ == "__main__":
    # Execute the entire automated workflow
    analyze_and_export_to_csv("./out/F18_edep.root")