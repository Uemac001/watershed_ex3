function run_weagets_all(station, varargin)
%RUN_WEAGETS_ALL Run WeaGETS for all Markov orders (1-3) and distributions (1-4).
%   run_weagets_all('GSTEIG')
%   run_weagets_all('GSTEIG','Years',1500,'Seed',1)
%
%   Writes <repo>/data/<station>_O<order>_D<distribution>_OUT.mat for each of
%   the 12 combinations. Distribution: 1 Exponential, 2 Gamma, 3 Skewed normal,
%   4 Mixed exponential. A combination that fails is reported and skipped.
%   From a shell (in the climate-impacts folder):
%   matlab -batch "addpath('WeaGETS/Ex3-WeaGETS'); run_weagets_all('GSTEIG')"

here = fileparts(mfilename('fullpath'));
root = fileparts(fileparts(here));

p = inputParser;
addParameter(p,'Years',1500);
addParameter(p,'Seed',1);
parse(p,varargin{:});
o = p.Results;

failed = {};
for order = 1:3
    for distr = 1:4
        out = fullfile(root,'data',sprintf('%s_O%d_D%d_OUT.mat',station,order,distr));
        fprintf('\n=== %s order %d distribution %d ===\n',station,order,distr);
        t = tic;
        try
            run_weagets_batch(station,'Years',o.Years,'Order',order, ...
                'Distribution',distr,'Seed',o.Seed,'Output',out);
            fprintf('done in %.0f s\n',toc(t));
        catch err
            fprintf(2,'FAILED: %s\n',err.message);
            failed{end+1} = sprintf('O%d_D%d: %s',order,distr,err.message); %#ok<AGROW>
        end
        close all
    end
end
if isempty(failed)
    fprintf('\nAll 12 combinations finished.\n');
else
    fprintf('\nFailed combinations:\n%s\n',strjoin(failed,newline));
end
end
