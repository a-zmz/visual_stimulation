
function varargout = visStimuli_GUI(varargin)
% visStimuli_GUI MATLAB code for visStimuli_GUI.fig
%      visStimuli_GUI, by itself, creates a new visStimuli_GUI or raises the existing
%      singleton*.
%
%      H = visStimuli_GUI returns the handle to a new visStimuli_GUI or the handle to
%      the existing singleton*.
%
%      visStimuli_GUI('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in visStimuli_GUI.M with the given input a§rguments.
%
%      visStimuli_GUI('Property','Value',...) creates a new visStimuli_GUI or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before visStimuli_GUI_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to visStimuli_GUI_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help visStimuli_GUI


% Last Modified by GUIDE v2.5 08-Jul-2013 13:59:42
Screen('Preference', 'SuppressAllWarnings', 1);

Screen('Preference', 'SkipSyncTests', 1);
% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @visStimuli_GUI_OpeningFcn, ...
                   'gui_OutputFcn',  @visStimuli_GUI_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before visStimuli_GUI is made visible.
function visStimuli_GUI_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to visStimuli_GUI (see VARARGIN)

% Choose default command line output for visStimuli_GUI
handles.output = hObject;


%------------------------TOM-CODE HERE-------------------------

% moving grating section
set(handles.driftTime,'String','2');
set(handles.staticTime,'String','0');
set(handles.spatFreq,'String','0.04');
set(handles.tempFreq,'String','1.0');

% push buttons

% retinotopy

% Parameters section
set(handles.distScreen,'String','25');
set(handles.widthScreen,'String','52');
set(handles.numberScreen,'String','0');
%set(handles.sizeImage,'String','800');
set(handles.stdevGauss,'String','10');
set(handles.trimGauss,'String','0.05');
set(handles.introTime,'String','0.5');

% save path
%set(handles.outputPath, 'String', 'C:\VisOutput');
set(handles.outputPath, 'String', 'D:\vis_stim_output');
set(handles.savePath,'String','yyyymmdd_exper_mouseID'); % this is the session name
set(handles.fileSuffix,'String','');

% for the chronic stim
set(handles.chronicOrient,'String','0');
set(handles.chronicTime,'String','0');

% for the custom stim
%set(handles.customSeq,'String','r,b,g,0,g,45,g,90,g,135,g,180,g,225,g,270,g,315,g,b');
set(handles.customSeq,'String','testsp');
set(handles.customGreyTime,'String','1');
set(handles.customBlackTime,'String','1');

%---------------------END TOM-CODE------------------------------ 

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes visStimuli_GUI wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = visStimuli_GUI_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;



function driftTime_Callback(hObject, eventdata, handles)
% hObject    handle to driftTime (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of driftTime as text
%        str2double(get(hObject,'String')) returns contents of driftTime as a double
timeDrift = str2double(get(hObject,'string'));
if isnan(timeDrift)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end


% --- Executes during object creation, after setting all properties.
function driftTime_CreateFcn(hObject, eventdata, handles)
% hObject    handle to driftTime (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function staticTime_Callback(hObject, eventdata, handles)
% hObject    handle to staticTime (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of staticTime as text
%        str2double(get(hObject,'String')) returns contents of staticTime as a double
timeStatic = str2double(get(hObject,'string'));
if isnan(timeStatic)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end


% --- Executes during object creation, after setting all properties.
function staticTime_CreateFcn(hObject, eventdata, handles)
% hObject    handle to staticTime (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function spatFreq_Callback(hObject, eventdata, handles)
% hObject    handle to spatFreq (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of spatFreq as text
%        str2double(get(hObject,'String')) returns contents of spatFreq as a double

spatFreq = str2double(get(hObject,'string'));

if isnan(spatFreq)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end



% --- Executes during object creation, after setting all properties.
function spatFreq_CreateFcn(hObject, eventdata, handles)
% hObject    handle to spatFreq (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function tempFreq_Callback(hObject, eventdata, handles)
% hObject    handle to tempFreq (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of tempFreq as text
%        str2double(get(hObject,'String')) returns contents of tempFreq as a double
cyclesPerSecond = str2double(get(hObject,'string'));
if isnan(cyclesPerSecond)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end


% --- Executes during object creation, after setting all properties.
function tempFreq_CreateFcn(hObject, eventdata, handles)
% hObject    handle to tempFreq (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end





% --- Executes on button press in retinotopy4x3.
function retinotopy4x3_Callback(hObject, eventdata, handles)
% hObject    handle to retinotopy4x3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of retinotopy4x3


% --- Executes on button press in retinotopyOther.
function retinotopy6x4_Callback(hObject, eventdata, handles)
% hObject    handle to retinotopyOther (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of retinotopyOther


% --- Executes when selected object is changed in numOrientationPanel.
function numOrientationPanel_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in numOrientationPanel 
% eventdata  structure with the following fields (see UIBUTTONGROUP)
%	EventName: string 'SelectionChanged' (read only)
%	OldValue: handle of the previously selected object or empty if none was selected
%	NewValue: handle of the currently selected object
% handles    structure with handles and user data (see GUIDATA)
switch get(eventdata.NewValue,'Tag') % Get Tag of selected object.
    case 'numOrient8'
        numOrient=8;% Code for when radiobutton1 is selected.
    case 'numOrient16'
        numOrient=16;
        % Code for when radiobutton2 is selected.
end


% --- Executes on button press in gaborOn.
function gaborOn_Callback(hObject, eventdata, handles)
% hObject    handle to gaborOn (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of gaborOn
if (get(hObject,'Value') == get(hObject,'Max'))
    gabor=1;
	% Radio button is selected-take appropriate action
end


% --- Executes on button press in gaborOff.
function gaborOff_Callback(hObject, eventdata, handles)
% hObject    handle to gaborOff (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of gaborOff
if (get(hObject,'Value') == get(hObject,'Max'))
	% Radio button is selected-take appropriate action
    gabor=0;
end


% --- Executes when selected object is changed in orientSeqPanel.
function orientSeqPanel_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in orientSeqPanel 
% eventdata  structure with the following fields (see UIBUTTONGROUP)
%	EventName: string 'SelectionChanged' (read only)
%	OldValue: handle of the previously selected object or empty if none was selected
%	NewValue: handle of the currently selected object
% handles    structure with handles and user data (see GUIDATA)

switch get(eventdata.NewValue,'Tag') % Get Tag of selected object.
    case 'randomSeq'
        randomOrder=1;% Code for when radiobutton1 is selected.
    case 'fixedSeq'
        randomOrder=0;
        % Code for when radiobutton2 is selected.
end

% --- Executes when selected object is changed in movingModePanel.
function movingModePanel_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in movingModePanel 
% eventdata  structure with the following fields (see UIBUTTONGROUP)
%	EventName: string 'SelectionChanged' (read only)
%	OldValue: handle of the previously selected object or empty if none was selected
%	NewValue: handle of the currently selected object
% handles    structure with handles and user data (see GUIDATA)
switch get(eventdata.NewValue,'Tag') % Get Tag of selected object.
    case 'uniDirectional'
        biDirectional=0;% Code for when radiobutton1 is selected.
    case 'biDirectional'
        biDirectional=1;
        % Code for when radiobutton2 is selected.
end

% --- Executes when selected object is changed in stimStylePanel.
function stimStylePanel_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in stimStylePanel 
% eventdata  structure with the following fields (see UIBUTTONGROUP)
%	EventName: string 'SelectionChanged' (read only)
%	OldValue: handle of the previously selected object or empty if none was selected
%	NewValue: handle of the currently selected object
% handles    structure with handles and user data (see GUIDATA)
switch get(eventdata.NewValue,'Tag') % Get Tag of selected object.
    case 'stimBW'
        stimStyle=0;% Code for when radiobutton1 is selected.
    case 'stimSin'
        stimStyle=1;
        % Code for when radiobutton2 is selected.
end


% --- Executes when selected object is changed in gaborPanel.
function gaborPanel_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in gaborPanel 
% eventdata  structure with the following fields (see UIBUTTONGROUP)
%	EventName: string 'SelectionChanged' (read only)
%	OldValue: handle of the previously selected object or empty if none was selected
%	NewValue: handle of the currently selected object
% handles    structure with handles and user data (see GUIDATA)

switch get(eventdata.NewValue,'Tag') % Get Tag of selected object.
    case 'gaborOn'
        gabor=1;% Code for when radiobutton1 is selected.
    case 'gaborOff'
        gabor=0;
        % Code for when radiobutton2 is selected.
end


function movieTotalDur_Callback(hObject, eventdata, handles)
% hObject    handle to distScreen (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of distScreen as text
%        str2double(get(hObject,'String')) returns contents of distScreen as a double
movieTotalDur = str2double(get(hObject,'string'));
if isnan(movieTotalDur)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end

% --- Executes during object creation, after setting all properties.
function movieTotalDur_CreateFcn(hObject, eventdata, handles)
% hObject    handle to driftTime (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


function noiseGridX_Callback(hObject, eventdata, handles)
% hObject    handle to distScreen (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of distScreen as text
%        str2double(get(hObject,'String')) returns contents of distScreen as a double
noiseGridX = str2double(get(hObject,'string'));
if isnan(noiseGridX)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end

% --- Executes during object creation, after setting all properties.
function noiseGridX_CreateFcn(hObject, eventdata, handles)
% hObject    handle to driftTime (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


function noiseGridY_Callback(hObject, eventdata, handles)
% hObject    handle to distScreen (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of distScreen as text
%        str2double(get(hObject,'String')) returns contents of distScreen as a double
noiseGridY = str2double(get(hObject,'string'));
if isnan(noiseGridY)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end

% --- Executes during object creation, after setting all properties.
function noiseGridY_CreateFcn(hObject, eventdata, handles)
% hObject    handle to driftTime (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


function noiseTotalDur_Callback(hObject, eventdata, handles)
% hObject    handle to distScreen (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of distScreen as text
%        str2double(get(hObject,'String')) returns contents of distScreen as a double
noiseTotalDur = str2double(get(hObject,'string'));
if isnan(noiseTotalDur)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end

% --- Executes during object creation, after setting all properties.
function noiseTotalDur_CreateFcn(hObject, eventdata, handles)
% hObject    handle to driftTime (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


function noiseFrameDur_Callback(hObject, eventdata, handles)
% hObject    handle to distScreen (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of distScreen as text
%        str2double(get(hObject,'String')) returns contents of distScreen as a double
noiseFrameDur = str2double(get(hObject,'string'));
if isnan(noiseFrameDur)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end

% --- Executes during object creation, after setting all properties.
function noiseFrameDur_CreateFcn(hObject, eventdata, handles)
% hObject    handle to driftTime (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

function distScreen_Callback(hObject, eventdata, handles)
% hObject    handle to distScreen (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of distScreen as text
%        str2double(get(hObject,'String')) returns contents of distScreen as a double
screenDist = str2double(get(hObject,'string'));
if isnan(screenDist)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end

% --- Executes during object creation, after setting all properties.
function distScreen_CreateFcn(hObject, eventdata, handles)
% hObject    handle to distScreen (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function widthScreen_Callback(hObject, eventdata, handles)
% hObject    handle to widthScreen (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of widthScreen as text
%        str2double(get(hObject,'String')) returns contents of widthScreen as a double
screenWidth = str2double(get(hObject,'string'));
if isnan(screenWidth)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end

% --- Executes during object creation, after setting all properties.
function widthScreen_CreateFcn(hObject, eventdata, handles)
% hObject    handle to widthScreen (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function numberScreen_Callback(hObject, eventdata, handles)
% hObject    handle to numberScreen (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of numberScreen as text
%        str2double(get(hObject,'String')) returns contents of numberScreen as a double
screenNumber = str2double(get(hObject,'string'));
if isnan(screenNumber)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end

% --- Executes during object creation, after setting all properties.
function numberScreen_CreateFcn(hObject, eventdata, handles)
% hObject    handle to numberScreen (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function sizeImage_Callback(hObject, eventdata, handles)
% hObject    handle to sizeImage (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of sizeImage as text
%        str2double(get(hObject,'String')) returns contents of sizeImage as a double
imageSize = str2double(get(hObject,'string'));
if isnan(imageSize)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end

% --- Executes during object creation, after setting all properties.
function sizeImage_CreateFcn(hObject, eventdata, handles)
% hObject    handle to sizeImage (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function stdevGauss_Callback(hObject, eventdata, handles)
% hObject    handle to stdevGauss (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of stdevGauss as text
%        str2double(get(hObject,'String')) returns contents of stdevGauss as a double
gaussStDev = str2double(get(hObject,'string'));
if isnan(gaussStDev)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end

% --- Executes during object creation, after setting all properties.
function stdevGauss_CreateFcn(hObject, eventdata, handles)
% hObject    handle to stdevGauss (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function trimGauss_Callback(hObject, eventdata, handles)
% hObject    handle to trimGauss (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of trimGauss as text
%        str2double(get(hObject,'String')) returns contents of trimGauss as a double
gaussTrim = str2double(get(hObject,'string'));
if isnan(gaussTrim)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end

% --- Executes during object creation, after setting all properties.
function trimGauss_CreateFcn(hObject, eventdata, handles)
% hObject    handle to trimGauss (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes when selected object is changed in retinotopyOptionsPanel.
function retinotopyOptionsPanel_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in retinotopyOptionsPanel 
% eventdata  structure with the following fields (see UIBUTTONGROUP)
%	EventName: string 'SelectionChanged' (read only)
%	OldValue: handle of the previously selected object or empty if none was selected
%	NewValue: handle of the currently selected object
% handles    structure with handles and user data (see GUIDATA)



function introTime_Callback(hObject, eventdata, handles)
% hObject    handle to introTime (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of introTime as text
%        str2double(get(hObject,'String')) returns contents of introTime as a double
timeIntro = str2double(get(hObject,'string'));
if isnan(timeIntro)
  errordlg('You must enter a numeric value','Bad Input','modal')
  uicontrol(hObject)
	return
end


% --- Executes during object creation, after setting all properties.
function introTime_CreateFcn(hObject, eventdata, handles)
% hObject    handle to introTime (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

function outputPath_Callback(hObject, eventdata, handles)
% hObject    handle to outputPath (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of savePath as text
%        str2double(get(hObject,'String')) returns contents of savePath as a double


% --- Executes during object creation, after setting all properties.
function outputPath_CreateFcn(hObject, eventdata, handles)
% hObject    handle to outputPath (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

function savePath_Callback(hObject, eventdata, handles)
% hObject    handle to savePath (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of savePath as text
%        str2double(get(hObject,'String')) returns contents of savePath as a double


% --- Executes during object creation, after setting all properties.
function savePath_CreateFcn(hObject, eventdata, handles)
% hObject    handle to savePath (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function chronicOrient_Callback(hObject, eventdata, handles)
% hObject    handle to chronicOrient (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of chronicOrient as text
%        str2double(get(hObject,'String')) returns contents of chronicOrient as a double


% --- Executes during object creation, after setting all properties.
function chronicOrient_CreateFcn(hObject, eventdata, handles)
% hObject    handle to chronicOrient (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% ----------------------------------------------------------------------------
% Callbacks for button presses

function type = determineGratingType(par)
    if par.movingReversal == 0
        type = stimuli.StimulusType.MovingGrating;
    else
        if par.chronicReversalFreq*par.timeDrift<2
           error('Increase reversal frequency or the drift time! (Freq * Time > 2)') 
        end
        type = stimuli.StimulusType.PhaseReversal;
    end


function runGratings_Callback(hObject, eventdata, handles)
    % initialise the variables
    par=getParam(handles);
    
    type = determineGratingType(par);
    par.stimulusDrawers = stimuli.calculateOrientations(...
        par.numOrient, par.chronicOrient, par.randomOrder, ...
        type);
    showStimuli(par);

function runMovie_Callback(hObject, eventdata, handles)
    par = getParam(handles);
    par.natMovie = 1;
    par.protocol = 'natural';
    
    movieChoice = get(handles.movie1, 'Value');
    if movieChoice == 1
        par.movieNum = 1;
    else
        movieChoice = get(handles.movie2, 'Value');
        if movieChoice == 1
            par.movieNum = 2;
        else
            par.movieNum = 3 ;
        end
    end 

    par.stimulusDrawers = [];
       
    showStimuli(par)

function runNoise_Callback(hObject, eventdata, handles)
    par = getParam(handles);
    par.sparseNoise = 1;
    par.protocol = 'visualNoise'; 
    
    noiseChoice = get(handles.black, 'Value');
    if noiseChoice == 1
        par.noiseClr = 0; % black
    else
        noiseChoice = get(handles.white, 'Value');
        if noiseChoice == 1
            par.noiseClr = 1; % white
        else
            par.noiseClr = 2; % Black & white
        end
    end 
    noiseType = get(handles.single, 'Value');
    if noiseType == 1
        par.noiseType = 0; % single
    else
        noiseType = get(handles.sparse, 'Value');
        if noiseType == 1
            par.noiseType = 1; % sparse
        else
            par.noiseType = 2; % dense
        end
    end 
        
    par.stimulusDrawers = [];

    showStimuli(par)
    
    
function runRetinotopy_Callback(hObject, eventdata, handles)
    par = getParam(handles);
    par.protocol = 'retinotopy';
    
    ret4x3State = get(handles.retinotopy4x3, 'Value');
    if ret4x3State == 1
        par.nCols = 4;
        par.nRows = 3;
    else
        par.nCols = 6;
        par.nRows = 4;
    end 
    if par.movingReversal == 0
        type = stimuli.StimulusType.MovingGrating;
    else
        if par.chronicReversalFreq*par.timeDrift<2
           error('Increase reversal frequency or the drift time! (Freq * Time > 2)') 
        end
        type = stimuli.StimulusType.PhaseReversal;
    end
    par.stimulusDrawers = stimuli.calculateOrientations(...
        par.numOrient, par.chronicOrient, par.randomOrder, ...
        type);

    showStimuli(par)


function runChronic_Callback(hObject, eventdata, handles)
    par=getParam(handles);
    par.protocol = 'chronicGrating';
    
    par.numOrient=1;
    par.timeDrift=par.chronicTime;  
    par.nCols=1;
    par.nRows=1;

    if (par.chronicReversal)
        if par.chronicReversalFreq*par.chronicTime<2
           error('Increase reversal frequency or the chronic time! (Freq * Time > 2)') 
        end
        stimulusType = stimuli.StimulusType.PhaseReversal;
    else
        stimulusType = stimuli.StimulusType.MovingGrating;
    end

    par.stimulusDrawers = stimuli.calculateOrientations(...
        par.numOrient, par.chronicOrient, par.randomOrder, stimulusType);
    
    showStimuli(par);


function runCustom_Callback(hObject, eventdata, handles)
   
par = getParam(handles); 

%Zahid Edit

      if strfind(par.customSeq,'explore')>0
           par.customSeq = '0,30,60,90,120,150,180,0,30,60,90,120,150,180,0,30,60,90,120,150,180,0,30,60,90,120,150,180,0,30,60,90,120,150,180,0,30,60,90,120,150,180,0,30,60,90,120,150,180';
      end

      
         if strfind(par.customSeq,'test')>0
               if strfind(par.customSeq,'2')>0
                   rep = 2;
               else
                   rep = 1;
               end
               if strfind(par.customSeq,'sp')>0
%                     try  
                       global spatial_freqstim 
                      
                       if length(spatial_freqstim)== 0
%                        spatial_freqstim = [0.01,0.02,0.04,0.08,0.16,0.32];
                       spatial_freqstim = [0.04,0.16];
                       spatial_freqstim = datasample(spatial_freqstim,length(spatial_freqstim),'Replace',false)
                       end
                       
%                     catch
%                         disp('error');
%                         global spatial_freqstim;
%                         spatial_freqstim = [0.01,0.02,0.04,0.08,0.16,0.32];
%                     end    
%                         r = randi([1 length(spatial_freqstim)],1,1);
                        par.spatFreq = spatial_freqstim(1);
                        spatial_freqstim(1) = [];
               end
               
         par.numorient = 12;
         orientationstim = (0:360/par.numorient:360-360/par.numorient);
         scarmbled_orientationstim = datasample(orientationstim,par.numorient,'Replace',false);    
         par.customSeq = 'b,g,';
            for index = [1:par.numorient]
            par.customSeq = [par.customSeq,num2str(scarmbled_orientationstim(index)),',g,'];   
            end
         par.customSeq = [par.customSeq,'b'];
         
        
         if rep == 2
         scarmbled_orientationstim = datasample(orientationstim,par.numorient,'Replace',false);     
         par.customSeq = [par.customSeq,',b,b,g,'];
            for index = [1:par.numorient]
            par.customSeq = [par.customSeq,num2str(scarmbled_orientationstim(index)),',g,'];   
            end
         par.customSeq = [par.customSeq,'b'];
         end
         
         end
   try
   type = determineGratingType(par);     
        par.stimulusDrawers = stimuli.parseCustomSequence(par.customSeq, type);
        par.Custom_seq=1;
        showStimuli(par);
    catch e
        if strcmp(e.identifier, 'stimuli:parseCustomSequence:InvalidValue')
            title = 'An error occurred when parsing the custom sequence string';
            uiwait(errordlg(e.message, title, 'modal'))
        else
            rethrow(e);
        end
    end
   
