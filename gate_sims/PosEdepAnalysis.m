clear;

% Initialize variables for energy deposition calculations
% use macroscopic data as peak, average, ioni percentage, brem percentage
% better for sorting data
numEnergies = 10;
avgpeak_ioni = zeros(numEnergies, 2);
avgpeak_brem = zeros(numEnergies, 2);
ionibremPercentages = zeros(numEnergies, 2);
energies = 0.1:0.1:1;

directory = dir("ElEdepData");
directory = directory(~[directory.isdir]);
sizes = [directory.bytes];
[~, sortedIdx] = sort(sizes);
directory = directory(sortedIdx);

for idx = 1:length(directory)
    % column names TotalEnergyDeposit, ProcessDefinedStep
    WaterEnergies = readtable("ElEdepData\"+directory(idx).name);
    eIoniWater = 1e6*WaterEnergies{(WaterEnergies.ProcessDefinedStep=="eIoni" & WaterEnergies.TotalEnergyDeposit>0), 2};
    eBremWater = 1e6*WaterEnergies{(WaterEnergies.ProcessDefinedStep=="eBrem" & WaterEnergies.TotalEnergyDeposit>0), 2};
    
    figure();
    max_power_ioni = ceil(log10(max(eIoniWater)));
    min_power_ioni = floor(log10(min(eIoniWater)));
    ioni_edges = logspace(min_power_ioni, max_power_ioni, 2000);
    histogram(eIoniWater, ioni_edges, 'Normalization', 'probability', 'EdgeColor', 'none');
    title("Ionization energy deposited by positron with "+num2str(energies(idx))+"MeV source energy");
    xlabel("Deposit Energy (eV)");
    ylabel("Normalized Probability");
    set(gca, 'XScale', 'log');
    [ionicounts, ~] = histcounts(eIoniWater, ioni_edges);
    
    max_power_brem = ceil(log10(max(eBremWater)));
    min_power_brem = floor(log10(min(eBremWater)));
    brem_edges = logspace(min_power_brem, max_power_brem, 200);
    % histogram(eBremWater, brem_edges, 'Normalization', 'probability', 'EdgeColor', 'none');
    % set(gca, 'XScale', 'log');
    [bremcounts, ~] = histcounts(eBremWater, brem_edges);

    ioniPercent = size(eIoniWater,1)/size(WaterEnergies,1); % proportion of stopping energy transfered as ionization
    bremPercent = size(eBremWater,1)/size(WaterEnergies,1); % proportion of stopping energy transfered as bremsstrahlung

    ionibremPercentages(idx,:) = [ioniPercent, bremPercent];
    [~,maxioniidx] = max(ionicounts);
    [~,maxbremidx] = max(bremcounts);
    avgpeak_ioni(idx,:) = [mean(eIoniWater),ioni_edges(maxioniidx)];
    avgpeak_brem(idx,:) = [mean(eBremWater),brem_edges(maxbremidx)];
end
% eMscWater = WaterEnergies{WaterEnergies.ProcessDefinedStep=="msc", 1};
% 
% SoftTissueEnergies = importdata("data\soft_tissue_ICRP_annihilation_energies.csv").data;
% AdiposeTissueEnergies = importdata("data\adipose_tissue_ICRP_annihilation_energies.csv").data;

% figure();
% histogram(eIoniWater, ioni_edges, 'Normalization', 'probability', 'EdgeColor', 'none');
% set(gca, 'XScale', 'log');
% xlabel("Energy (eV)");
% ylabel("Relative Probability");
% title("Normalized Distribution of 1MeV e+ Deposited Energy in Water by Ionization");
% 
% figure();
% histogram(eBremWater, brem_edges, 'Normalization', 'probability', 'EdgeColor', 'none');
% set(gca, 'XScale', 'log');
% xlabel("Energy (eV)");
% ylabel("Relative Probability");
% title("Normalized Distribution of 1MeV e+ Deposited Energy in Water by Bremsstrahlung");

figure();
hold on;
plot(energies, avgpeak_ioni(:,1), 'red', LineStyle='--');
plot(energies, avgpeak_ioni(:,2), 'blue');
hold off;
legend("average edep", "peak edep");
title("Average and Peak ionization Energy transfer for 1MeV positron source");
xlabel("Initial Energy (MeV)");
ylabel("Deposit Energy (eV)");

figure();
hold on;
plot(energies, avgpeak_brem(:,1), 'red', LineStyle='--');
plot(energies, avgpeak_brem(:,2), 'blue');
hold off;
legend("average edep", "peak edep");
title("Average and Peak bremsstrahlung Energy transfer for 1MeV positron source");
xlabel("Initial Energy (MeV)");
ylabel("Deposit Energy (eV)");


figure();
hold on;
plot(energies, ionibremPercentages(:,1));
plot(energies, ionibremPercentages(:,2));
hold off;
legend("ionization", "bremsstrahlung");
set(gca, 'YScale', 'log');
title("Proportion of Ionization and Bremsstrahlung events");
xlabel("Initial Energy (MeV)");
ylabel("Proportion");

% figure(3);
% 
% histogram(eMscWater, 200, 'Normalization', 'probability');
% % set(gca, 'YScale', 'log');
% xlabel("Energy (MeV)");
% ylabel("Relative Probability");
% title("Normalized Probability of Energy Deposited in Water by Multiple Scattering");

% figure(2);
% 
% histogram(SoftTissueEnergies, 200, 'Normalization', 'probability');
% set(gca, 'YScale', 'log');
% xlabel("Energy (MeV)");
% ylabel("Relative Probability");
% title("Normalized Probability of Annihilation in Soft Tissue");
% figure(3);
% 
% histogram(AdiposeTissueEnergies, 200, 'Normalization', 'probability');
% set(gca, 'YScale', 'log');
% xlabel("Energy (MeV)");
% ylabel("Relative Probability");
% title("Normalized Probability of Annihilation in Adipose Tissue");
% 

