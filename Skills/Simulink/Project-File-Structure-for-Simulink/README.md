# Simulink Project File Structure

## Project Organization

This Simulink project follows a structured organization pattern to maintain consistency and facilitate collaboration. The project uses a standardized folder structure for models and their associated artifacts.

## Complete Project Folder Structure

```
Project Root/
├── cache/                 # Cached files and temporary data (automatically used by Simulink)
├── codegen/               # Generated code from models (automatically used by Simulink)
├── data/                  # Project-level data files
├── doc/                   # Project-level documentation
├── internal/              # Internal utilities and templates for the project itself
│   ├── createNewModel.m          # Model creation utility function
│   ├── newModelTemplate.slx      # Template for new models
│   └── newSubsystemTemplate.slx  # Template for new subsystems
├── models/                # Contains all Simulink models and subsystems
├── requirements/          # Project-level requirements
├── test/                  # Project-level test files
├── utilities/             # Utility functions and scripts
├── work/                  # Working directory for temporary files
├── resources/             # DO NOT EDIT - automatically managed by MATLAB
├── SimulinkProjectFileStructure.prj  # MATLAB Project file
└── README.md              # This file
```

## Model Folder Structure (Created by createNewModel)

Each model or subsystem created using the `createNewModel` function follows a consistent folder structure within the `models/` directory:

```
models/
└── <ModelName>/           # Root folder for the model
    ├── <ModelName>.slx    # Simulink model/subsystem file
    ├── <ModelName>_harnessInfo.xml  # DO NOT EDIT - Test harness information (if Simulink Test available), automatically maintained by Simulink Test 
    ├── data/              # Data and configuration files
    │   └── <ModelName>.sldd  # Simulink Data Dictionary, attached to <ModelName>.slx
    ├── doc/               # Documentation specific to this model
    ├── requirements/      # Requirements and specifications for this model
    └── test/              # Test-related artifacts
        ├── harnesses/     # Test harnesses
        │   └── <ModelName>_harness.slx  # Test harness (if Simulink Test available)
        ├── data/          # Test data files
        └── <ModelName>_Tests.mldatx  # Test Manager file (if Simulink Test available)
```

## Using the createNewModel Function

The `createNewModel` function automates the creation of new models or subsystems with the proper folder structure and associated files.

### Syntax

```matlab
% Create a new model (default)
createNewModel("MyModelName")

% Explicitly create a model
createNewModel("MyModelName", "Type", "Model")

% Create a subsystem
createNewModel("MySubsystemName", "Type", "Subsystem")
```

### Parameters

- **mdlName** (required): String specifying the name of the model or subsystem to create
- **Type** (optional): Either "Model" or "Subsystem" (default: "Model")

### What the Function Creates

When you run `createNewModel`, it automatically:

1. **Creates the complete folder structure** under `models/<ModelName>/`:
   - `models/<ModelName>/` - Root folder for the model
   - `models/<ModelName>/data/` - For data dictionaries and configuration
   - `models/<ModelName>/doc/` - For model-specific documentation
   - `models/<ModelName>/requirements/` - For requirements documents
   - `models/<ModelName>/test/` - For test artifacts
   - `models/<ModelName>/test/harnesses/` - For test harnesses
   - `models/<ModelName>/test/data/` - For test data

2. **Creates the Simulink model/subsystem**:
   - Uses templates from the `internal/` folder (`newModelTemplate.slx` or `newSubsystemTemplate.slx`)
   - Saves as `<ModelName>.slx` in `models/<ModelName>/`

3. **Creates and links a Simulink Data Dictionary**:
   - Creates `<ModelName>.sldd` in `models/<ModelName>/data/`
   - Automatically attaches it to the model

4. **Creates test artifacts** (if Simulink Test is licensed):
   - Test harness: `<ModelName>_harness.slx` in `models/<ModelName>/test/harnesses/`
   - Harness info: `<ModelName>_harnessInfo.xml` in `models/<ModelName>/`
   - Test file: `<ModelName>_Tests.mldatx` in `models/<ModelName>/test/`

5. **Adds all created files and folders to the project**:
   - Automatically registers all files with the Simulink project
   - Adds all folders to the project path

### Example Usage

```matlab
% Create a new model called "ControlSystem"
createNewModel("ControlSystem")

% This creates the following structure:
% models/
% └── ControlSystem/
%     ├── ControlSystem.slx
%     ├── ControlSystem_harnessInfo.xml  # (if Simulink Test available)
%     ├── data/
%     │   └── ControlSystem.sldd
%     ├── doc/
%     ├── requirements/
%     └── test/
%         ├── harnesses/
%         │   └── ControlSystem_harness.slx  # (if Simulink Test available)
%         ├── data/
%         └── ControlSystem_Tests.mldatx  # (if Simulink Test available)
```

### Prerequisites

- Must be run within an active Simulink Project
- Project must have a `models/` folder at the root level
- Templates (`newModelTemplate.sltx` and `newSubsystemTemplate.sltx`) must exist in the `internal/` folder
- Simulink Test license required for test artifact creation (optional - function will still work without it)

### Benefits

- **Consistency**: All models follow the same organizational structure
- **Automation**: Reduces manual setup time and potential errors
- **Best Practices**: Enforces separation of concerns (data, docs, tests, requirements)
- **Scalability**: Makes it easy to manage multiple models in large projects
- **Project Path Management**: Automatically adds all folders to the project path for easy access

### Notes

- The function will create all folders even if they remain empty initially
- All created artifacts are automatically added to the Simulink project
- Test artifacts are only created if Simulink Test toolbox is licensed
- The model templates in the `internal/` folder can be customized to match your organization's standards
- Generated code from models will be stored in the project-level `codegen/` folder