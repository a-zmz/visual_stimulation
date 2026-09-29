function [tfSparseNoise] = GenerateSparseNoiseStimulus(  vnUnitSize, vnNumUnits, vnSeed, ...
                                                         nNumFrames, vfPixelValues)

% GenerateSparseNoiseStimulus - FUNCTION Generate a sparse noise stimulus
%
% Usage: [tfSparseNoise] = GenerateSparseNoiseStimulus(  vnUnitSize, vnNumUnits, vnSeed ...
%                                                        <, nNumFrames, vfPixelValues>)
%
% This function generates a sparse noise stimulus movie, for use in
% characterising a receptive field, for example.  By default it will generate a
% grey field with single black and white pixels on each frame.  The optional
% argument 'vfPixelValues' can be used to control this.  'vfPixelValues' has the
% format ['fBackground' 'vfStimValues'], where 'vfStimValues' is a vector of
% pixel values to insert over the background.  The default value is [0.5 0 1],
% such that a greay field is created with single balck (0) and white (1) pixels.
% You can define single white pixels on a black field with [0 1], or single
% black pixels on a grey field with [0.5 0], for example.  An arbitrary number
% of pixel values can be provided.
%
% 'vnUnitSize' is a vector ['nXSize' 'nYSize'] which defines the size of a
% stimulus unit in texture pixels. 'vnNumUnits' is a vector ['nXUnits'
% 'nYUnits'] which defines the size of the entire stimulus in units.
% 'vnSeed' is used to seed the random number generator, to obtain a repeatable
% stimulus.  If a vector of seeds is provided, a compound sequence of sparse
% noise sequences will be generated, built by combining the individual seeded
% sequences. If 'vnSeed' is empty then the sequence is ordered.
%
% The optional argument 'nNumFrames' defines the total number of frames to
% generate.  By default, the stimulus will be long enough to present every
% stimulus combination.

% Author: Dylan Muir <dylan@ini.phys.ethz.ch>
% Created: 27th August, 2010

% -- Defaults

DEF_vfPixelValues = [0.5 0 1];


% -- Check arguments

if (nargin < 3)
   disp('*** GenerateSparseNoiseStimulus: Incorrect usage');
   help GenerateSparseNoiseStimulus;
   sca;
   return;
end

if (~exist('vfPixelValues', 'var') || isempty(vfPixelValues))
   vfPixelValues = DEF_vfPixelValues;
end

if (~exist('nNumFrames', 'var'))
   nNumFrames = [];
end


% - Extract background value and pixel values
fBackground = vfPixelValues(1);
vfPixelValues = vfPixelValues(2:end);
nNumPixelValues = numel(vfPixelValues);

% - Compute total number of possible stimuli
nNumStimuli = prod(vnNumUnits) * nNumPixelValues;

% - Compute total pixel size
vnStimSizePixels = vnUnitSize .* vnNumUnits;

% - Build a compound sequence, if required
if (numel(vnSeed) > 1)
   if (isempty(nNumFrames) || (nNumFrames > nNumStimuli))
      nThisNumFrames = [];
   else
      % - A very short sequence was requested, so just generate a single
      % sequence
      nThisNumFrames = nNumFrames;
      vnSeed = vnSeed(1);
   end
   
   % - Generate the first sequence
   tfSparseNoise = GenerateSparseNoiseStimulus(vnUnitSize, vnNumUnits, vnSeed(1), nThisNumFrames, [fBackground; vfPixelValues(:)]);

   for (nSeedID = 2:numel(vnSeed))
      % - Build a sparse noise sequence for each seed
      tfSparseNoise = cat(3, tfSparseNoise, GenerateSparseNoiseStimulus(vnUnitSize, vnNumUnits, vnSeed(nSeedID), nNumFrames, [fBackground; vfPixelValues(:)]));
   end
   
   % - Take 'nNumFrames' frames, if requested   
   if (~isempty(nNumFrames))
      tfSparseNoise = tfSparseNoise(:, :, nNumFrames);
   end

else
   % -- Build a single sparse noise sequence

   if (~exist('nNumFrames', 'var') || isempty(nNumFrames))
      nNumFrames = nNumStimuli;
   end
   
   
   % -- Generate stimulus
      
   % - Seed RNG
   if (~isempty(vnSeed))
      rand('twister', vnSeed(1)); %#ok<RAND>
      % - Find a random ordering of stimulus IDs
      mStimIDs = [(1:nNumStimuli)' rand(nNumStimuli, 1)];
      mStimIDs = sortrows(mStimIDs, 2);   
      vnStimIDs = mStimIDs(:, 1);
   else
       vnStimIDs = (1:nNumStimuli);
   end
   

   
   % - Convert to x, y, stim indices
   [mnStimLoc(:, 1) mnStimLoc(:, 2) mnStimLoc(:, 3)] = ind2sub([vnNumUnits nNumPixelValues], vnStimIDs);
   
   % - Construct stimuli
   tfSparseNoise = fBackground * ones([vnStimSizePixels nNumStimuli]);
   
   mnXStimLocs(:, 1) = (mnStimLoc(:, 1) - 1) * vnUnitSize(1) + 1;
   mnXStimLocs(:, 2) = mnXStimLocs(:, 1) + vnUnitSize(1) - 1;
   mnYStimLocs(:, 1) = (mnStimLoc(:, 2) - 1) * vnUnitSize(2) + 1;
   mnYStimLocs(:, 2) = mnYStimLocs(:, 1) + vnUnitSize(2) - 1;
   
   if (nargout == 0)
      hFig = figure;
      colormap gray;
   end
   
   
   for (nFrame = 1:nNumFrames)
      tfSparseNoise(mnXStimLocs(nFrame, 1):mnXStimLocs(nFrame, 2), mnYStimLocs(nFrame, 1):mnYStimLocs(nFrame, 2), nFrame) = vfPixelValues(mnStimLoc(nFrame, 3));
      
      if (nargout == 0)
         figure(hFig);
         clf;
         imagesc(tfSparseNoise(:, :, nFrame)');
         axis equal tight off;
         caxis([min([fBackground vfPixelValues]), max([fBackground vfPixelValues])]);
         colorbar;
         drawnow;
      end
   end
end

% --- END of GenerateSparseNoise.m ---
