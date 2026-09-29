function [par, data_all] = SparseNoise(par)

% Get parameters ----------------------------------------------------------

screenSize = [0 0 par.imageSizeX par.imageSizeY]; % get screen size
hWindow = par.w; % get window handle 
screenGrid = [par.noiseGridX, par.noiseGridY]; % get x by y grid
numFrames = floor(par.noiseTotalDur/par.noiseFrameDur); % sort out how many frames you can present in total stim time
blackTime = par.customBlackTime;
greyTime = par.customGreyTime;
noiseType = par.noiseType;

% default settings
stimClrs = [150 0 255]; % grey (background), black(noise), white(noise)
if noiseType==1 
    sparseNumStim = floor((screenGrid(1)*screenGrid(2))/4); % defines how sparse is sparse. Default = 1/4 of grid (divided by 4)
elseif noiseType==2     
    sparseNumStim = floor((screenGrid(1)*screenGrid(2))/1.5);  % defines how dense is dense. Default = 2/3 of grid (divided by 1.5)
end

% Main --------------------------------------------------------------------

% Stimulus parameters
% set stimuli colours
if par.noiseClr == 0
    noiseClrs = [stimClrs(2) stimClrs(2)];
elseif par.noiseClr == 1
    noiseClrs = [stimClrs(3) stimClrs(3)];
elseif par.noiseClr == 2
    noiseClrs = stimClrs(2:3);
end
sqClrs = randi(2, [1, numFrames]); % randomize order (in case two colours where choosen)

% Set stimuli position on screen
sqSize = floor([screenSize(3)/screenGrid(1), screenSize(4)/screenGrid(2)]);
posCentresX = (sqSize(1)/2): sqSize(1): screenSize(3)-(sqSize(1)/2);
posCentresY = (sqSize(1)/2): sqSize(1): screenSize(4)-(sqSize(1)/2);

sqPos = combvec(posCentresX, posCentresY); % get all possible screen positions in grid
sqPos = sqPos(:, randperm(size(sqPos,2))); % randomize positions for presentation
while numFrames > size(sqPos,2) % if there are more frames needed than possible unique screen positions, reuse positions
    sqPos = [sqPos,  sqPos(:, randperm(size(sqPos,2)))]; %#ok<AGROW>
end

% if more than single stimulis per frame (sparse or dense noise), randomize positions
if noiseType==1 || noiseType==2 % sparse or dense noise
    rndIndx = randperm(size(sqPos,2));
    for i=1:ceil(numFrames*sparseNumStim/size(sqPos,2));
        rndIndx = [rndIndx, randperm(size(sqPos,2))]; %#ok<AGROW>
    end
    rndIndx2 = nan(sparseNumStim, numFrames);
    iFrame=1;
    while iFrame < numFrames +1
        rndIndx2(:,iFrame) = rndIndx(iFrame*sparseNumStim:iFrame*sparseNumStim+(sparseNumStim-1));
        iFrame = iFrame+1;
    end
    sqPosSparse = nan(2, sparseNumStim, numFrames);
    for iFrame = 1:numFrames
        sqPosSparse(:,:,iFrame) = sqPos(:,rndIndx2(:,iFrame)');
    end
    sqClrs = randi(2, [sparseNumStim, numFrames]); % randomize order (in case two colours where choosen) 
    sqSize = reshape(repmat(sqSize, 1,sparseNumStim),2,[]); 
end


% Initiate stimTimes counting
stimTimes = nan(6, 1);
frameTimes = nan(numFrames,1);

% Debugging: get window handle and screen size for 
%[hWindow, screenSize] = Screen('OpenWindow', 0, 0, [0 0 500 500]); 

% start with black/grey screen
stimTimes(1) = GetSecs(); % trial start
pause(blackTime);
Screen('FillRect', hWindow, 150, screenSize);
stimTimes(2) = Screen('Flip', hWindow);
pause(greyTime);

% Present stimulus
if noiseType==0 % single noise block at a time
    for iFrame = 1:numFrames;
        Screen('DrawDots', hWindow, sqPos(:,iFrame), sqSize(1), noiseClrs(sqClrs(iFrame)));
        frameTimes(iFrame) = Screen('Flip', hWindow);
        pause(par.noiseFrameDur);
    end
elseif noiseType==1 || noiseType==2 % sparse or dense noise
    for iFrame = 1:numFrames;
        Screen('DrawDots', hWindow, sqPosSparse(:,:,iFrame), sqSize(1,:), repmat(noiseClrs(sqClrs(:,iFrame)),3,1));
        frameTimes(iFrame) = Screen('Flip', hWindow);
        pause(par.noiseFrameDur);
    end
else
    error('Unrecognized noise type');
end

% end with grey/black screen
Screen('FillRect', hWindow, 150, screenSize);
stimTimes(4) = Screen('Flip', hWindow);
pause(greyTime);
Screen('FillRect', hWindow, 0, screenSize);
stimTimes(5) = Screen('Flip', hWindow);
pause(blackTime);
stimTimes(6) = GetSecs(); % trial end
%clear Screen;

stimTimes(3) = frameTimes(1); % retrieve start of stim period
frameTimes = frameTimes-stimTimes(1);
stimTimes = stimTimes-stimTimes(1);

% save metadata
par.numNoiseFrames = numFrames;
% save data
data_all.time = [stimTimes(1:2); frameTimes; stimTimes(4:end-1)]; 
[stimType{1:numFrames,1}] = deal('N'); 
data_all.type = ['U'; 'U'; stimType; 'U'; 'U'];
if noiseType==0 % single noise block at a time
    data_all.position = sqPos(:,1:numFrames);
    data_all.color = noiseClrs(sqClrs);
elseif  noiseType==1 || noiseType==2 % sparse or dense noise
    data_all.position = sqPosSparse(:,:,1:numFrames);
    data_all.color = noiseClrs(sqClrs); 
end
