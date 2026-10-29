clear;


directory = dir("full");
directory = directory(~[directory.isdir]);
numEnergies = numel(directory);
peak_range = zeros(numEnergies, 1);
avg_range = zeros(numEnergies, 1);

energies = 0.05:0.05:0.95;
wall = 9.95;

for idx = 1:length(directory)
    % directory(idx).name
    rawWaterPos = importdata("full\"+directory(idx).name).data;

    WaterRangeR = sqrt(rawWaterPos(:,1).^2 + rawWaterPos(:,2).^2 + rawWaterPos(:,3).^2);
    atwall = ((abs(rawWaterPos(:,1)) >= wall) | abs(rawWaterPos(:,2)) >= wall | abs(rawWaterPos(:,3)) >= wall);
    filteredRange = WaterRangeR(~atwall, 1);
    
    [counts, edges] = histcounts(filteredRange, 2000);
    [maxCount, maxIdx] = max(counts);
    peak_range(idx) = edges(maxIdx);
    avg_range(idx) = mean(filteredRange);
    
    % histogram(filteredRange, 2000, 'Normalization', 'probability');
    % set(gca, 'YScale', 'log');
    % xlabel("Distance (mm)");
    % ylabel("Relative Probability");
    % title("Normalized Distribution of "+num2str(energies(idx))+"MeV positron Annihilation Range in Water");
    % 
    % figure();
    % 
    % scatter3(rawWaterPos(~atwall,1),rawWaterPos(~atwall,2),rawWaterPos(~atwall,3), 10, 'filled');
    % title("Range of "+num2str(energies(idx))+"MeV positrons from origin");
end
figure();
histogram(filteredRange, 2000, 'Normalization', 'probability');
% set(gca, 'YScale', 'log');
xlabel("Distance (mm)");
ylabel("Relative Probability");
title("Normalized Distribution of 0.95MeV e+ Range in Water");

figure();
histogram(filteredRange, 2000, 'Normalization', 'probability');
set(gca, 'YScale', 'log');
xlabel("Distance (mm)");
ylabel("Relative Probability");
title("Log Normalized Distribution of 0.95MeV e+ Range in Water");

figure();

scatter3(rawWaterPos(~atwall,1),rawWaterPos(~atwall,2),rawWaterPos(~atwall,3), 1, 'filled');
title("Displacement of 1MeV e+ from origin");

avg_range = sort(avg_range);
peak_range = sort(peak_range);

figure();
hold on;
plot(energies, avg_range, 'red');
plot(energies, peak_range, 'blue');
hold off;

title("peak and average displacement from mono source for e+ of a given source energy");
xlabel("Source Energy (MeV)");
ylabel("Range (mm)");
legend("Avg", "Peak");

% hold on;
% scatter([0],[0], 50, 'filled', 'red');
% hold off;

% figure(2);
% 
% histogram(SoftTissueEnergies, 200, 'Normalization', 'probability');
% set(gca, 'YScale', 'log');
% xlabel("Energy (MeV)");
% ylabel("Relative Probability");
% title("Normalized Probability of Annihilation in Soft Tissue");
% 
% figure(3);
% 
% histogram(AdiposeTissueEnergies, 200, 'Normalization', 'probability');
% set(gca, 'YScale', 'log');
% xlabel("Energy (MeV)");
% ylabel("Relative Probability");
% title("Normalized Probability of Annihilation in Adipose Tissue");


