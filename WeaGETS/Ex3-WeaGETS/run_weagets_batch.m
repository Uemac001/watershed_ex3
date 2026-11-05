function run_weagets_batch(station, varargin)
%RUN_WEAGETS_BATCH Run WeaGETS without the dialogs of RUN_WeaGETS.m.
%   run_weagets_batch('LATTERBACH')
%   run_weagets_batch('LATTERBACH','Years',1500,'Order',2,'Distribution',4,'Seed',1)
%
%   Reads <station>_WEAGETS_IN.mat next to this file and writes
%   <repo>/data/<station>_OUT.mat (variables gP, gTmax, gTmin).
%   From a shell:
%   matlab -batch "addpath('WeaGETS/Ex3-WeaGETS'); run_weagets_batch('LATTERBACH')"
%
%   Options (same choices as the RUN_WeaGETS.m dialogs):
%     Threshold    daily precipitation threshold [mm] (default 0.1)
%     Years        years to generate (default 1500 = 50 series of 30 years)
%     Order        Markov chain order 1, 2 or 3 (default 1)
%     Distribution 1 Exponential, 2 Gamma, 3 Skewed normal, 4 Mixed exponential (default 2)
%     Seed         random seed for reproducible output (default: not set)
%     Output       output .mat path (default <repo>/data/<station>_OUT.mat)

here = fileparts(mfilename('fullpath'));
root = fileparts(fileparts(here));

p = inputParser;
addParameter(p,'Threshold',0.1);
addParameter(p,'Years',1500);
addParameter(p,'Order',1);
addParameter(p,'Distribution',2);
addParameter(p,'Seed',[]);
addParameter(p,'Output',fullfile(root,'data',[station '_OUT.mat']));
parse(p,varargin{:});
o = p.Results;

addpath(here);
filenamein = fullfile(here,[station '_WEAGETS_IN.mat']);
if ~isfile(filenamein)
    error('Input file not found: %s',filenamein);
end
outdir = fileparts(o.Output);
if ~isempty(outdir) && ~isfolder(outdir)
    mkdir(outdir);
end
if ~isempty(o.Seed)
    rng(o.Seed);
end

TempScheme = 1;   % as in RUN_WeaGETS.m
switch o.Order
    case 1
        [idistr,ap00,ap10,par,A,B,aC0,aC1,aC2,aD1,aD2,sC0,sC1,sC2,sD1,sD2,thr,order] = ...
            analyzer_order1_norad_no(filenamein,o.Threshold,o.Distribution);
        generator_order1_norad_no(o.Output,o.Years,TempScheme,idistr,ap00,ap10,par,A,B, ...
            aC0,aC1,aC2,aD1,aD2,sC0,sC1,sC2,sD1,sD2,thr,order);
    case 2
        [idistr,ap000,ap010,ap100,ap110,par,A,B,aC0,aC1,aC2,aD1,aD2,sC0,sC1,sC2,sD1,sD2,thr,order] = ...
            analyzer_order2_norad_no(filenamein,o.Threshold,o.Distribution);
        generator_order2_norad_no(o.Output,o.Years,TempScheme,idistr,ap000,ap010,ap100,ap110,par,A,B, ...
            aC0,aC1,aC2,aD1,aD2,sC0,sC1,sC2,sD1,sD2,thr,order);
    case 3
        [idistr,ap0000,ap0010,ap0100,ap0110,ap1000,ap1010,ap1100,ap1110,par,A,B,aC0,aC1,aC2,aD1,aD2,sC0,sC1,sC2,sD1,sD2,thr,order] = ...
            analyzer_order3_norad_no(filenamein,o.Threshold,o.Distribution);
        generator_order3_norad_no(o.Output,o.Years,TempScheme,idistr,ap0000,ap0010,ap0100,ap0110, ...
            ap1000,ap1010,ap1100,ap1110,par,A,B,aC0,aC1,aC2,aD1,aD2,sC0,sC1,sC2,sD1,sD2,thr,order);
    otherwise
        error('Order must be 1, 2 or 3');
end
fprintf('WeaGETS output written to %s\n',o.Output);
end
