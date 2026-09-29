%
% Set up screens for drawing stimuli, draw them, and save the parameter setup
% and stimuli timing details into the output file.
%
% Created for Nathalie Rochefort's lab by Tom Mayo, Summer 2013,
% NeuroInformatics DTC @ Edinburgh
%
% Edited and improved by
%   Lukas Solanka <lukas.solanka@ed.ac.uk>
%   Paolo Puggioni <p.puggioni@sms.ed.ac.uk>
%
function showStimuli(par)
    import stimuli.CustomStimulus;
    
    %% added by Tom
    try 
     ports=serialportlist("available")';
     %arduinoObj = serialport("COM12",115200);
     arduinoObj = serialport("COM3",115200);
    catch
     warning('Error')
    end


    %%
    stimulusDrawers = par.stimulusDrawers;
    screenWidth     = par.screenWidth;
    nCols           = par.nCols;
    nRows           = par.nRows;

    try
        % --------------------------------------------------------------------
        %         This code has to be before the trigger waiting loop
        % --------------------------------------------------------------------
        AssertOpenGL;
        dummy=GetSecs;
        Screen('Preference', 'VisualDebugLevel', 1); % to avoid the white welcome screen
        [white, black, grey] = CustomStimulus.getColors(par.screenNumber);
        Screen('Preference', 'Verbosity', 1); % 1 = only display PTB critical errors (use 2 to also display warnings)
        Screen('Preference', 'VBLTimestampingMode', -1); % avoid error message about timestamp accuracy with multi-screen displays. high precison timestamping does not work under these conditions.
        % Screen('Preference', 'SkipSyncTests', 1); %uncomment if recording stimulus from desktop or testing
        [w screenRect] = Screen('OpenWindow', par.screenNumber, grey); %, [0, 0, 400, 400]);

        % Indicate to the user we might be busy
        ShowCursor('SandClock');

        
    %Added by Zahid
    default = 't';
    
    explore = 'f';
    xstart = 960; %center is 960
    ystart = 540;  %center is 540las
    angle = 20;

    
        % Create individual rectangles, depending on the nRows and nCols
        % parameters
       
        origscreenwidth = screenRect(3) - screenRect(1);
        origscreenheight = screenRect(4) - screenRect(2);
        origspatFreq = par.spatFreq;        
    
    if default == 't'
        screenWidth  = floor((screenRect(3) - screenRect(1)));
        screenHeight = floor((screenRect(4) - screenRect(2)));
        explore = 'f'; 
    else
        screenWidth  = floor((screenRect(3) - screenRect(1))*angle/104);
        screenHeight = screenWidth;%floor((screenRect(4) - screenRect(2))*angle/72);
        par.spatFreq = origspatFreq*(angle/104);
    end

        if par.splitScreen
            screenWidth = screenWidth / 2;
        end
        
        width        = floor(screenWidth / nCols);
        height       = floor(screenHeight / nRows);

        par.imageSizeX = screenWidth;
        par.imageSizeY = screenHeight;
        


        destRectList = zeros(nRows * nCols, 4);
        it = 1;
        for row = [1:nRows]
            for col = [1:nCols]
                
                if default == 't'
                destRectList(it, 1) = (col-1) * width;
                destRectList(it, 2) = (row-1) * height;
                destRectList(it, 3) = (col) * width;
                destRectList(it, 4) = (row) * height;
                else
                destRectList(it, 1) = floor(xstart-width/2);
                destRectList(it, 2) = floor((origscreenheight-ystart)-height/2);
                destRectList(it, 3) = floor(xstart+width/2);
                destRectList(it, 4) = floor((origscreenheight-ystart)+height/2);
                end
                
                it = it + 1;
            end
        end

        % Initialise the drawers. This should be before the actual drawing
        % begins.
        par.w = w;
        if par.natMovie == 1
            if par.movieNum == 1;
                moviefile = 'C:\Program Files\VisStim\NaturalMovies\movie1.avi';
            elseif par.movieNum == 2;
                moviefile = 'C:\Program Files\VisStim\NaturalMovies\movie2.avi';
            elseif par.movieNum == 3;
                moviefile = 'C:\Program Files\VisStim\NaturalMovies\movie3.avi';
            else
                error('Do not recognize movie number');
            end

            write(arduinoObj,'2',"char");  %switch on the IR LED
          
            [par.hMovie, par.movieDur, par.moviefps]=Screen('OpenMovie', par.w, moviefile);
            
%            
        elseif par.sparseNoise ~= 1 && par.natMovie ~= 1
            for drawer = stimulusDrawers
                drawer.setDrawingParameters(par);
            end
        end
      
        % --------------------------------------------------------------------

        % Reset the cursor before we start
        ShowCursor('Arrow');
        
        % --------------------------------------------------------------------
        warning('off');
        % Trigger waiting loop
        if par.waitForTrigger
            display('Waiting for Trigger...');
            s = daq.createSession('ni');
            s.addDigitalChannel('Dev1', 'Port1/Line0:7', 'InputOnly');
             
            a=0;
            
            while a<1 
              %pause(0.0005);
              testt=s.inputSingleScan;
              a=testt(end);
              
            end
            
        end
                
        warning('on');
        par.Trigger_time=GetSecs;
        par.Trigger_datenum = now;
        c=clock;
        screenNumber = par.screenNumber;
        % correct for windows assigned screen numbers not matching matlab
%         if par.screenNumber==2
%             screenNumber = 3;
%         elseif par.screenNumber==3
%             screenNumber = 2;
%         end
        fprintf('Trial Start: Presenting %s on screen %d\n', par.protocol, screenNumber)
        % --------------------------------------------------------------------
    

        % --------------------------------------------------------------------
        %                               DRAW

            
            
        if par.sparseNoise == 1
            [par, data_all] = stimuli.SparseNoise(par);
        elseif par.natMovie == 1
            par.arduinoObj = arduinoObj;
            [par, data_all] = stimuli.NaturalMovie(par);
        else
            Seq_time = {};
            ii=0;
            
         
         
         for numRect = [1:nRows*nCols] 
            dstRect = destRectList(numRect, :);
            n_draws=0;
            % Animationloop:
            write(arduinoObj,'2',"char");
            for drawer = stimulusDrawers
                % added by Tom 
                n_draws=n_draws+1;
                write(arduinoObj,'1',"char");  %switch on the IR LED

                if explore == 't'
                pointerxy = get(0, 'PointerLocation');
                    if pointerxy(1)>1
                    destRectList(1, 1) = floor(pointerxy(1)-width/2);
                    destRectList(1, 2) = floor((origscreenheight-pointerxy(2))-height/2);
                    destRectList(1, 3) = floor(pointerxy(1)+width/2);
                    destRectList(1, 4) = floor((origscreenheight-pointerxy(2))+height/2);
                    lastpointerxy = pointerxy;
                    elseif pointerxy(1)==1
                    width = pointerxy(2)*2;     
                    height = pointerxy(2)*2;     
                    destRectList(1, 1) = floor(lastpointerxy(1)-width/2);
                    destRectList(1, 2) = floor((origscreenheight-lastpointerxy(2))-height/2);
                    destRectList(1, 3) = floor(lastpointerxy(1)+width/2);
                    destRectList(1, 4) = floor((origscreenheight-lastpointerxy(2))+height/2);
                    end
                dstRect = destRectList(numRect, :);
                disp(['Last point x,y: ', num2str(lastpointerxy)])
                disp(['Angle: ', num2str(floor(104*width/(screenWidth)))])
                end
                ii=ii+1;
                Seq_time{ii}=drawer.draw(dstRect);
            end
            write(arduinoObj,'3',"char");
        end

        end
        
        par.spatFreq = origspatFreq;
        % --------------------------------------------------------------------

        par.End_time=GetSecs;
        par.End_datenum = now;
    catch
        Screen('CloseAll');
        Priority(0);
        psychrethrow(psychlasterror);
    end
    write(arduinoObj,'1',"char");
    write(arduinoObj,'3',"char");  %switch off the IR LED
    Priority(0);
    Screen('CloseAll');





    % --------------------SAVE THE ORDER AND TIME OF EVENTS------------------
  

    
    formatOut='yyyymmdd_HHMMSS';
    
    name1=datestr(c,formatOut);
    namefolder=datestr(c,'yyyymmdd');
    
    % Check to see that user input 'Session Name' matches the current date
    sesUserInput = textscan(par.sessionName, '%c', 8);
    sesUserInputDate = datenum(sesUserInput,'yyyymmdd');
    
    sesDateChk = sesUserInputDate - now;
    if sesDateChk> 0.8 || sesDateChk< -1
        choice = menu('Your "Session Name" feels wrong to me, are you sure you want to continue?',...
            'Yes, I have things under control (saves metadata file)', 'No, get me out of here (metadata file will be discarded)');
        if choice == 2 || choice == 0
            error('Fix your Session Name before continuing. The first 8 charaters should be todays date in yyyymmdd format')
        else
        end
    end
    
    % Save file in folders designated by user input to visStimuli_GUI
    if ~exist(fullfile(par.outputPath,par.sessionName,namefolder), 'file')
        mkdir(fullfile(par.outputPath,par.sessionName,namefolder));
    end
    
    outputFilePath=fullfile(par.outputPath,par.sessionName,namefolder);
    
    file_name = fullfile(outputFilePath,[name1 par.fileSuffix,'.txt']);
    file_name_mat=fullfile(outputFilePath,[name1 par.fileSuffix,'.mat']);
    fid = fopen (file_name,'w');

    % Print parameters of stimulus to txt file
    if default == 'f'
    fprintf(fid,'PARAMETERS:\n');
%     fprintf(fid,'Angle (deg): %.0f\n ', angle);
%     fprintf(fid,'xPosition (1920pix): %.0f\n ', xstart);
%     fprintf(fid,'yPosition (1080pix): %.0f\n ', ystart);
    fprintf(fid,['Angle (deg): %.0f\n ',...
                'xPosition (1920pix): %.0f\n ',...
                'yPosition (1080pix): %.0f\n '],...
                angle,...
                xstart,...
                ystart);                
             
    end            

    if par.numOrient==1  % THESE ARE THE CHRONIC STIMULI
        if par.chronicReversal==0 %grating
            fprintf(fid,'Chronic stimulus\n');   
            printGratingTiming(fid, par);
            fprintf(fid,'Chronic panel, orientation (deg): %.0f\n', ...
                    par.chronicOrient);
        elseif par.chronicReversal==1
            %Seq_time=Seq_time{1}; %phase rev
            fprintf(fid,'Chronic stimulus - Phase Reversal\n');   
            printReversalGratingTiming(fid, par);
            fprintf(fid,'Chronic panel, orientation (deg): %.0f\n',par.chronicOrient);
        end
        
    elseif nRows>1 % THIS IS THE RETINOTROPY
        if par.movingReversal == 0 %grating
            fprintf(fid,'Retinotopy, row x col: %d x %d\n',nRows,nCols);
            printGratingTiming(fid, par);
            printGratingParams(fid, par);
        elseif par.movingReversal == 1 %phase rev
            fprintf(fid,'Retinotopy, row x col: %d x %d - Phase Reversal\n',nRows,nCols);
            printReversalGratingTiming(fid, par);
            printGratingParams(fid, par);
        end   
            
    elseif isfield(par,'Custom_seq') % THIS IS THE CUSTOM SEQUENCE
            if par.Custom_seq==1
                if par.movingReversal == 0 % grating
                    fprintf(fid,'Custom Sequence: %s \n',par.customSeq); 
                    printGratingTiming(fid, par)
                else % phase reversal
                    fprintf(fid,'Custom Sequence: %s - Phase reversal\n', ...
                            par.customSeq); 
                    printReversalGratingTiming(fid, par)
                end
                printGratingParams(fid, par);
            else
                error(['Custom sequence printing requested ', ...
                       'but par.Custom_seq == 0!']);
            end
            
            
    else % THIS IS THE ORIENTATION LIST
        if par.movingReversal == 0 %grating
            fprintf(fid,'Moving gratings \n');         
            printGratingTiming(fid, par)
            printGratingParams(fid, par)
        elseif par.movingReversal == 1 %phase reversal
            fprintf(fid,'Phase reversal \n');         
            printReversalGratingTiming(fid, par)
            printGratingParams(fid, par)
        end
    end
    
    fprintf(fid,'\nTime(s)\tOrient.(deg)\tType\n');
    
    if par.sparseNoise == 0 && par.natMovie == 0 % create data_all struct. sparseNoise and natural movie created separately
        time_vec=[];
        angle_vec=[];
        type_vec={};
        ll=0;
        kk=0;
        while kk<length(Seq_time)
            kk=kk+1;
            
            if isprop(Seq_time{kk},'startTime') % THIS IS FOR UNIFORM GRAY BLACK SCREEN
                time_static=Seq_time{kk}.startTime - par.Trigger_time;
                fprintf(fid,'%3.4f\t%3.1f\t%s\n',time_static,0,'Uniform');
                time_vec=[time_vec; time_static];
                type_vec=[type_vec; 'U'];
                angle_vec=[angle_vec;0];
                
            else % THIS IS FOR THE REST
                time_static=Seq_time{kk}.staticStartT - par.Trigger_time;
                fprintf(fid,'%3.4f\t%3.1f\t%s\n',time_static,Seq_time{kk}.angle-90,'Static');
                time_vec=[time_vec; time_static];
                type_vec=[type_vec; 'S'];
                angle_vec=[angle_vec;Seq_time{kk}.angle-90];
                
                time_forward=Seq_time{kk}.forwardStartT - par.Trigger_time;
                fprintf(fid,'%3.4f\t%3.1f\t%s\n',time_forward,Seq_time{kk}.angle-90,'Forward');
                time_vec=[time_vec; time_forward];
                type_vec=[type_vec; 'F'];
                angle_vec=[angle_vec;Seq_time{kk}.angle-90];
                
                
                if Seq_time{kk}.bidirectional==1
                    time_backward=Seq_time{kk}.backwardStartT - par.Trigger_time;
                    fprintf(fid,'%3.4f\t%3.1f\t%s\n',time_backward,Seq_time{kk}.angle-90,'Backward');
                    time_vec=[time_vec; time_backward];
                    type_vec=[type_vec; 'B'];
                    angle_vec=[angle_vec;Seq_time{kk}.angle-90];
                end
            end
        end
        
        fprintf(fid,'%3.4f\tEnd\n',par.End_time-par.Trigger_time);
        
        data_all.time=time_vec;
        data_all.type=type_vec;
        data_all.angle=angle_vec;
    end
     save(file_name_mat,'par','data_all')
     
     % Make sure we actually did save the file
     if ~exist(file_name_mat,'file')
         msgbox('Couldn''t save metadata file', 'Error');
         error('Couldn''t save metadata file: %s',file_name_mat);
     end
     
    fclose(fid);
    fprintf('Trial End: %s\n\n', name1) 

function printGratingTiming(fid, par)
    fprintf(fid, ['Drift time (s): %.1f, ', ...
                  'Static time(s): %.1f, ', ...
                  'Spatial Frequency (cyc/deg):%.2f, ', ...
                  'Temporal Frequency (cyc/s): %.1f\n'], ...
                  par.timeDrift, ...
                  par.timeStatic, ...
                  par.spatFreq, ...
                  par.cyclesPerSecond);

function printReversalGratingTiming(fid, par)
    fprintf(fid, ['Drift time (s): %.1f, ', ...
                  'Static time(s): %.1f, ', ...
                  'Spatial Frequency (cyc/deg):%.2f, ', ...
                  'Reversal Frequency (cyc/s): %.1f\n'], ...
                  par.timeDrift, ...
                  par.timeStatic, ...
                  par.spatFreq, ...
                  par.chronicReversalFreq);

function printGratingParams(fid, par)
    fprintf(fid, ...
            ['N orient.: %d, ', ...
             'Random (1=YES,0=NO): %d, ', ...
             'Bidirectional (1=YES,0=NO): %d, ', ...
             'Stim. Style (1=sin,0=square): %d, ', ...
             'Gabor (1=YES,0=NO): %d\n'], ...
            par.numOrient, ...
            par.randomOrder, ...
            par.biDirectional, ...
            par.stimStyle, ...
            par.gabor);
