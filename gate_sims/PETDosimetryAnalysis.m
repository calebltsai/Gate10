clear;

% F18_full.csv, Sc44_full.csv, Ga68_full.csv, Rb82_full.csv
% % NOTE: column names "ParticleName", "TotalEnergyDeposit", "ProcessDefinedStep", "PostPosition_X", "PostPosition_Y", "PostPosition_Z", "EventID"

file = "full\Rb82_9T.csv";
ds = datastore(file);
EventData = tall(ds);
% df = readtable(file);

% % NOTE: main data/visualization filters here
% % NOTE: add posfilter or not
% posfilter = gather(EventData.ParticleName == "e+");
energyfilter = gather(EventData.TotalEnergyDeposit > 0);
columnsToKeep = {'TotalEnergyDeposit', 'ProcessDefinedStep', 'EventID', 'PostPosition_X', 'PostPosition_Y', 'PostPosition_Z'};
xlim = 10; ylim = 10; zlim = 20;
posfilter = gather(EventData.PostPosition_X <= xlim & EventData.PostPosition_X >= -xlim ...
    & EventData.PostPosition_Y <= ylim & EventData.PostPosition_Y >= -ylim ...
    & EventData.PostPosition_Z <= zlim & EventData.PostPosition_Z >= -zlim);
EventData = EventData(posfilter, columnsToKeep);
X_event = gather(EventData.PostPosition_X);
Y_event = gather(EventData.PostPosition_Y);
Z_event = gather(EventData.PostPosition_Z);

% % NOTE: can filter energy depending on type of event, scale based on type
% of energy transfer (Effective dose)
edeps = gather(EventData.TotalEnergyDeposit);

% % NOTE: end of track filtering
% range_data = groupsummary(df, 'EventID', {@(x) x(end)});

% % NOTE: for normalization/energy purposes
% Activity_Bq = 50000;       % source.activity = 50000*Bq
% Run_Time_Sec = 0.5;        % sim.run_timing_intervals = 0.5 sec

% % NOTE: filter events here
grid_size = 400; % Number of voxels per axis
x_edges = linspace(-xlim, xlim, grid_size+1);
y_edges = linspace(-ylim, ylim, grid_size+1);
z_edges = linspace(-zlim, zlim, grid_size+1);
subs_x = discretize(X_event, x_edges);
subs_y = discretize(Y_event, y_edges);
subs_z = discretize(Z_event, z_edges);
subs = [subs_x, subs_y, subs_z];

% dists = sqrt(range_data.PostPosition_X.^2 + range_data.PostPosition_Y.^2 + range_data.PostPosition_Z.^2);
dosemap = accumarray(subs, edeps, [length(x_edges)-1, length(y_edges)-1, length(z_edges)-1], @sum, 0);
% dosemap = log(dosemap);

x_centers = (x_edges(1:end-1) + x_edges(2:end)) / 2;
y_centers = (y_edges(1:end-1) + y_edges(2:end)) / 2;
z_centers = (z_edges(1:end-1) + z_edges(2:end)) / 2;
[X_grid, Y_grid, Z_grid] = meshgrid(x_centers, y_centers, z_centers);

figure('Color', 'w');
V_plot = permute(dosemap, [2, 1, 3]); 

% % NOTE: find slices to visualize
slices_x = mean(x_centers);
slices_y = mean(y_centers);
slices_z = [mean(z_centers)-1, mean(z_centers), mean(z_centers)+1];
h = slice(X_grid, Y_grid, Z_grid, V_plot, slices_x, slices_y, slices_z);

% % NOTE: color/heatmap visualization
set(h, 'EdgeColor', 'none');
colormap(hot); % Hot scale matches energy deposition fields perfectly
colorbar; ylabel(colorbar, 'Total Cumulative Energy Deposited');
view(3); grid on; shading interp;
xlabel('X Position'); ylabel('Y Position'); zlabel('Z Position');
title('Cumulative Voxel Energy Density Mapping');

% clim([0,1]);
axis equal;

% figure();
% scatter3(x_event,y_event,z_event, 10, 'filled');