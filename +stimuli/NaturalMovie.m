function [par, data_all] = NaturalMovie(par)

% Get parameters ----------------------------------------------------------

screenSize = [0 0 par.imageSizeX par.imageSizeY]; % get screen size
hWindow = par.w; % get window handle 
hMovie = par.hMovie; % get movie handle
playDuration = par.movieTotalDur; % sort out how many frames you can present in total stim time
blackTime = par.customBlackTime;
greyTime = par.customGreyTime;

% par.moviefps
timesLoop = floor(playDuration/par.movieDur); % sort out how many time to play movie in total stim time

% default settings
Screen('Preference', 'Verbosity', 0);
soundVolume = 0; % mute=0; volume 0 to 1 scale;
playRate = 1;
loop = 1; % Set movie to loop.

% Debugging: get window handle and screen size for 
%[hWindow, screenSize] = Screen('OpenWindow', 0, 0, [0 0 720 405]);
% moviefile = 'D:\OneDrive\Work Stuff\Projects\Multimodal_VIP_SST\NaturalMovies\Edited\MiceInCage1.avi';
%[hMovie, par.movieDur, par.moviefps]=Screen('OpenMovie', hWindow, moviefile);
%timesLoop = 2; % sort out how many time to play movie in total stim time

% Timing variables:
% 1 = trial start
% 2 = pre-movie gray onset
% 3 = movie start sync pulse
% 4 = movie end sync pulse
% 5 = post-movie gray onset
% 6 = post-movie black onset
% 7 = trial end
stimTimes = nan(7, 1);
loopTimes = nan(timesLoop, 1);

% -------------------------------------------------------------------------
% Start with black / gray screen
% -------------------------------------------------------------------------
stimTimes(1) = GetSecs(); % trial start
WaitSecs(blackTime);
Screen('FillRect', hWindow, 150, screenSize);
stimTimes(2) = Screen('Flip', hWindow);

WaitSecs(greyTime);

% -------------------------------------------------------------------------
% Movie start sync pulse, after gray and before movie starts
% -------------------------------------------------------------------------
if isfield(par, 'arduinoObj')
    write(par.arduinoObj, '1', "char");
    stimTimes(3) = GetSecs();
else
    warning('No arduino object found in par. Sync pulse not sent.');
    stimTimes(3) = NaN;
end

% -------------------------------------------------------------------------
% Movie playback
% -------------------------------------------------------------------------
% loop through movie as many times as will fit fully into total stim duration (does not play partial movies)
for iLoop = 1:timesLoop;
    Screen('PlayMovie', hMovie, playRate, loop, soundVolume);% Start playback engine
    
    % Playback loop: Runs until end of movie
    t = 0;
    t1 = GetSecs();
    loopTimes(iLoop) = GetSecs(); % get start of loop period
    
    while t <= par.movieDur % play all frames
        % Wait for next movie frame, retrieve texture handle to it
        tex = Screen('GetMovieImage', hWindow, hMovie);
%         % Valid texture returned? A negative value means end of movie reached:
%         if tex<=0
%             sca
%             
%             % We're done, break out of loop:
%             break;
%         end
        Screen('DrawTexture', hWindow, tex, [], screenSize);  % Draw the new texture immediately to screen
        t = Screen('Flip', hWindow); % Update display
        t = t-t1;
        
        Screen('Close', tex); % Release texture
    end
    
    Screen('PlayMovie', hMovie, 0); % Stop playback
end

% -------------------------------------------------------------------------
% Movie end sync pulse
% -------------------------------------------------------------------------
if isfield(par, 'arduinoObj')
    write(par.arduinoObj, '1', "char");
    stimTimes(4) = GetSecs(); % end-of-movie sync pulse time
else
    warning('No arduino object found in par. End sync pulse not sent.');
    stimTimes(4) = NaN;
end

Screen('CloseMovie', hMovie); % Close movie

% -------------------------------------------------------------------------
% End with gray / black screen
% -------------------------------------------------------------------------
Screen('FillRect', hWindow, 150, screenSize);
stimTimes(5) = Screen('Flip', hWindow);

WaitSecs(greyTime);

Screen('FillRect', hWindow, 0, screenSize);
stimTimes(6) = Screen('Flip', hWindow);

WaitSecs(blackTime);

stimTimes(7) = GetSecs(); % trial end
%clear Screen;

% -------------------------------------------------------------------------
% Normalize times to trial start
% -------------------------------------------------------------------------
loopTimes = loopTimes-stimTimes(1);
stimTimes = stimTimes-stimTimes(1);

% output data
data_all.time = [stimTimes(1:3); loopTimes; stimTimes(4:end-1)];

[stimType{1:timesLoop,1}] = deal('M'); % M for Movie

%data_all.type = ['U'; 'U'; stimType; 'U'; 'U'];
data_all.type = [{'TrialStart'}; ...
                 {'PreMovieGray'}; ...
                 {'MovieStartSync'}; ...
                 stimType; ...
                 {'MovieEndSync'}; ...
                 {'PostMovieGray'}; ...
                 {'PostMovieBlack'}];

end