%
%   Parse GUI parameters.
%
%   Copyright (C) 2013, NeuroAgile.
%       Authors: Paolo Puggioni <p.paolo321@gmail.com>
%

% Get all parameters set in the GUI
function par=getParam(handles)
    % Set default parameters:
    par.natMovie = 0;
    par.sparseNoise = 0;
    par.nCols = 1;
    par.nRows = 1;
    par.protocol = 'gratings';

    % Get parameters from GUI
    par.spatFreq = str2double(get(handles.spatFreq,'String'));
    par.cyclesPerSecond = str2double(get(handles.tempFreq,'String'));
    par.timeStatic = str2double(get(handles.staticTime,'String'));
    par.timeDrift = str2double(get(handles.driftTime,'String'));
    % 
    % % the button ones too....
    switch get(get(handles.numOrientationPanel,'SelectedObject'),'Tag')
        case 'numOrient8',  par.numOrient = 8;
        otherwise, par.numOrient = 16;
    end

    switch get(get(handles.gaborPanel,'SelectedObject'),'Tag')
        case 'gaborOn',  par.gabor = 1;
        otherwise, par.gabor = 0;
    end

    switch get(get(handles.stimStylePanel,'SelectedObject'),'Tag')
        case 'stimBW',  par.stimStyle = 0;
        otherwise, par.stimStyle = 1;
    end

    par.biDirectional = 0;
    par.movingReversal = 0;
    switch get(get(handles.movingModePanel,'SelectedObject'),'Tag')
        case 'biDirectional',  par.biDirectional = 1;
        case 'phaseReversal',  par.biDirectional = 0; par.movingReversal = 1;
        otherwise, par.biDirectional = 0;
    end

    switch get(get(handles.orientSeqPanel,'SelectedObject'),'Tag')
        case 'randomSeq',  par.randomOrder = 1;
        otherwise, par.randomOrder = 0;
    end


    % and those from the parameters box.....
    par.screenDist     = str2double(get(handles.distScreen,'String'));
    par.screenWidth    = str2double(get(handles.widthScreen,'String'));
    par.screenNumber   = str2double(get(handles.numberScreen,'String'));
%     % correct for windows assigned screen numbers not matching matlab 
%     if par.screenNumber==2
%         par.screenNumber = 3;
%     elseif par.screenNumber==3
%         par.screenNumber = 2;
%     end
    par.gaussStDev     = str2double(get(handles.stdevGauss,'String'));
    par.gaussTrim      = str2double(get(handles.trimGauss,'String'));
    par.timeIntro      = str2double(get(handles.introTime,'String'));
    par.waitForTrigger = get(handles.triggerWaitCheckBox, 'Value');
    par.splitScreen    = get(handles.splitScreenCheckBox, 'Value');

    % those for the Natural Movie
    par.movieTotalDur       = str2double(get(handles.movieTotalDur, 'String'));
    
    % those for the Sparse Noise
    par.noiseGridX          = str2double(get(handles.noiseGridX, 'String'));
    par.noiseGridY          = str2double(get(handles.noiseGridY, 'String'));
    par.noiseTotalDur       = str2double(get(handles.noiseTotalDur, 'String'));
    par.noiseFrameDur       = str2double(get(handles.noiseFrameDur, 'String'));
    
    % those for the chronic stim
    par.chronicOrient       = str2double(get(handles.chronicOrient,'String'));
    par.chronicTime         = str2double(get(handles.chronicTime,'String'));
    par.chronicReversal     = get(handles.phaseReversalCheckBox, 'Value');
    par.chronicReversalFreq = str2double(get(handles.tempFreq, 'String')); % old variable reversalFreqEdit. Updated to use tempFreq for all
    
    % those for Custom stim
    par.customSeq       = get(handles.customSeq, 'String');
    par.customGreyTime  = str2double(get(handles.customGreyTime, 'String'));
    par.customBlackTime = str2double(get(handles.customBlackTime, 'String'));
    par.randGrey        = randfixedsum(5,1,54,5,15);
    
    % and the save path
    par.sessionName = get(handles.savePath,'String');
    par.outputPath = get(handles.outputPath, 'String');
    par.fileSuffix =get(handles.fileSuffix,'String');

end


