clear;

WaterEnergies = importdata("data\water_annihilation_energies.csv").data;
SoftTissueEnergies = importdata("data\soft_tissue_ICRP_annihilation_energies.csv").data;
AdiposeTissueEnergies = importdata("data\adipose_tissue_ICRP_annihilation_energies.csv").data;

figure(1);

histogram(WaterEnergies, 200, 'Normalization', 'probability');
set(gca, 'YScale', 'log');
xlabel("Energy (MeV)");
ylabel("Relative Probability");
title("Normalized Probability of Annihilation in Water");

figure(2);

histogram(SoftTissueEnergies, 200, 'Normalization', 'probability');
set(gca, 'YScale', 'log');
xlabel("Energy (MeV)");
ylabel("Relative Probability");
title("Normalized Probability of Annihilation in Soft Tissue");
figure(3);

histogram(AdiposeTissueEnergies, 200, 'Normalization', 'probability');
set(gca, 'YScale', 'log');
xlabel("Energy (MeV)");
ylabel("Relative Probability");
title("Normalized Probability of Annihilation in Adipose Tissue");


