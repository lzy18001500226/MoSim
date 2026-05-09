function createNewModel(mdlName, options)
%% createNewModel creates a model or subsystem and set of folders in a Project
% This function takes as input a string that will be the name of a new Simulink model or subsystem.
% It is meant to be run in a Project that has a "models" folder at the project root level.
% A folder with the model/subsystem name will be created in the project's "models"
% folder, along with a Simulink Data Dictionary (.sldd) file of the same name in the "data" subfolder,
% attached to the model/subsystem, and a set of folders for artifacts related to the model/subsystem.
%
% Syntax:
%   createNewModel(mdlName)
%   createNewModel(mdlName, "Type", "Model")
%   createNewModel(mdlName, "Type", "Subsystem")
%
% Input Arguments:
%   mdlName - Name of the model or subsystem to create
%   
% Name-Value Arguments:
%   "Type" - Type of system to create ("Model" or "Subsystem"). Default is "Model"

arguments
    mdlName string
    options.Type string {mustBeMember(options.Type, ["Model", "Subsystem"])} = "Model"
end

% Create the folder structure for the new model
Prj        = currentProject;
PrjRoot    = Prj.RootFolder;
ModelDir   = fullfile(PrjRoot,"models");

ModelRootDir   = fullfile(ModelDir,mdlName);
DataDir        = fullfile(ModelRootDir,"data");
DocDir         = fullfile(ModelRootDir,"doc");
RequirementDir = fullfile(ModelRootDir,"requirements");
TestDir        = fullfile(ModelRootDir,"test");
TestHarnessDir = fullfile(TestDir,"harnesses");
TestDataDir    = fullfile(TestDir,"data");

folders = {ModelRootDir,DataDir,DocDir,RequirementDir,TestDir,TestHarnessDir,TestDataDir};

% Create the folders and add them to the Project
for i=1:numel(folders)
    mkdir(folders{i});
    addFile(Prj,folders{i});
    addPath(Prj,folders{i});
end

% Create a new model or subsystem based on the Type option
if strcmpi(options.Type, "Model")
    % Create a new model from model template in the project
    new_system(mdlName,"FromTemplate","newModelTemplate"); % This model template file is in the "internal" folder in the project. You can replace with your own template.
else
    % Create a new subsystem
    new_system(mdlName,"FromTemplate","newSubsystemTemplate");
end

mdlPath = fullfile(ModelRootDir,strcat(mdlName,".slx"));
save_system(mdlPath);
addFile(Prj,mdlPath); % add it to the project

% Create Simulink Data Dictionary and put it in the "data" folder
slddObjPath = fullfile(DataDir,strcat(mdlName,".sldd"));
Simulink.data.dictionary.create(slddObjPath);
addFile(Prj,slddObjPath); % add it to the project

% Attach the sldd to the model
load_system(mdlName);
[~,slddName,slddExt] = fileparts(slddObjPath);
set_param(mdlName,"DataDictionary",strcat(slddName,slddExt));
save_system(mdlName);
close_system(mdlName);

% Create model harness and Simulink Test file (if Simulink Test is available)
if license("test","simulink_test")
    % Create test harness
    load_system(mdlName);
    HarnessName = strcat(mdlName,"_harness");
    sltest.harness.create(mdlName,Name=HarnessName,...
        Source="Inport",Sink="Outport",...
        SaveExternally=true,HarnessPath=TestHarnessDir);
    save_system(mdlName);
    close_system(mdlName);

    HarnessFullPath = fullfile(TestHarnessDir,strcat(HarnessName,".slx"));
    HarnessInfoPath = fullfile(ModelRootDir,strcat(mdlName,"_harnessInfo.xml"));

    % Create Test Manager file
    TestFileName = strcat(mdlName,"_Tests.mldatx");
    TestFilePath = fullfile(TestDir,TestFileName);
    testFileObj = sltest.testmanager.TestFile(TestFilePath);

    % Files to add to project
    testFiles = {HarnessFullPath,HarnessInfoPath,TestFilePath};
    % Create the folders and add them to the Project
    for i=1:numel(testFiles)
        addFile(Prj,testFiles{i});
    end
end

end