// SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <carb/logging/Log.h>

#include <isaacsim/asset/importer/urdf/ImportHelpers.h>
#include <isaacsim/asset/importer/urdf/MeshImporter.h>
#include <isaacsim/core/includes/utils/Path.h>

#include <OmniClient.h>
#include <algorithm>
#include <cmath>
#include <filesystem>
#include <map>
#include <omniverse_asset_converter.h>
#include <set>
#include <stack>
#include <tinyxml2.h>
#include <unordered_set>

namespace isaacsim
{
namespace asset
{
namespace importer
{
namespace urdf
{
using namespace isaacsim::core::includes::utils::path;
std::string StatusToString(OmniConverterStatus status)
{
    switch (status)
    {
    case OmniConverterStatus::OK:
        return "OK";
    case OmniConverterStatus::CANCELLED:
        return "Cancelled";
    case OmniConverterStatus::IN_PROGRESS:
        return "In Progress";
    case OmniConverterStatus::UNSUPPORTED_IMPORT_FORMAT:
        return "Unsupported Format";
    case OmniConverterStatus::INCOMPLETE_IMPORT_FORMAT:
        return "Incomplete File";
    case OmniConverterStatus::FILE_READ_ERROR:
        return "Asset Not Found";
    case OmniConverterStatus::FILE_WRITE_ERROR:
        return "Output Path Cannot be Opened";
    case OmniConverterStatus::UNKNOWN:
        return "Unknown";
    default:
        return "Unknown";
    }
}


const static size_t INVALID_MATERIAL_INDEX = SIZE_MAX;


pxr::TfToken getMaterialToken(pxr::UsdStageWeakPtr stage, const pxr::SdfPath& materialPath)
{
    // Get the material object from the stage
    pxr::UsdShadeMaterial material = pxr::UsdShadeMaterial(stage->GetPrimAtPath(materialPath));

    // If the material doesn't exist, return an empty token
    if (!material)
    {
        return pxr::TfToken();
    }

    auto shaderPrim = *material.GetPrim().GetChildren().begin();
    // Get the shader object for the material
    pxr::UsdShadeShader shader(shaderPrim);
    if (!shader)
    {
        return pxr::TfToken();
    }

    std::stringstream ss;
    for (const auto& attr : shaderPrim.GetAttributes())
    {
        ss << "<";
        ss << attr.GetTypeName() << " : " << attr.GetName() << " = ";

        pxr::VtValue value;
        if (attr.Get(&value))
        {
            ss << value << ">\n";
        }
        else
        {
            ss << ">\n"; // Handle cases where the attribute has no value
        }
    }

    // Create a TfToken from the token string
    pxr::TfToken token(ss.str());
    return token;
}

void moveAndBindMaterial(const pxr::UsdStageRefPtr& sourceStage,
                         const pxr::UsdStageRefPtr& dstStage,
                         const pxr::SdfPath& rootPath,
                         const pxr::SdfPath& sourcePath,
                         const pxr::SdfPath& dstPath,
                         std::map<pxr::TfToken, pxr::SdfPath>& materialList)
{
    auto sourceImageable = sourceStage->GetPrimAtPath(sourcePath);
    auto dstImageable = dstStage->GetPrimAtPath(dstPath);
    pxr::UsdShadeMaterialBindingAPI bindingAPI(sourceImageable);
    pxr::UsdShadeMaterialBindingAPI::DirectBinding directBinding = bindingAPI.GetDirectBinding();
    pxr::UsdShadeMaterial material = directBinding.GetMaterial();
    if (material)
    {
        pxr::TfToken materialToken = getMaterialToken(sourceStage, material.GetPrim().GetPath());
        pxr::SdfPath materialPath;
        if (materialList.count(materialToken))
        {
            materialPath = materialList[materialToken];
        }
        else
        {
            materialPath = pxr::SdfPath(isaacsim::asset::importer::urdf::GetNewSdfPathString(
                dstStage, rootPath.AppendChild(pxr::TfToken("Looks"))
                              .AppendChild(pxr::TfToken(material.GetPath().GetName()))
                              .GetString()));
            pxr::SdfCopySpec(sourceStage->GetRootLayer(), material.GetPath(), dstStage->GetRootLayer(), materialPath);
            materialList.emplace(materialToken, materialPath);
        }

        pxr::UsdShadeMaterial newMaterial = pxr::UsdShadeMaterial(dstStage->GetPrimAtPath(materialPath));
        if (newMaterial)
        {
            bindingAPI = pxr::UsdShadeMaterialBindingAPI(dstImageable);
            bindingAPI.Bind(newMaterial);
        }
    }
}

void moveMeshAndMaterials(const pxr::UsdStageRefPtr& sourceStage,
                          const pxr::UsdStageRefPtr& dstStage,
                          const pxr::SdfPath& rootPath,
                          const pxr::SdfPath& meshPath,
                          const pxr::SdfPath& targetPrimPath,
                          std::map<pxr::TfToken, pxr::SdfPath>& materialList)
{
    // Get the mesh from stage A

    // Create a new mesh in stage B
    pxr::UsdGeomXform newMesh = pxr::UsdGeomXform::Define(dstStage, targetPrimPath);
    if (!newMesh)
    {
        CARB_LOG_ERROR("Error: Could not create new mesh at path %s", targetPrimPath.GetText());
        return;
    }

    // Copy the mesh attributes from stage A to stage B
    pxr::SdfCopySpec(sourceStage->GetRootLayer(), meshPath, dstStage->GetRootLayer(), targetPrimPath);
}


pxr::SdfPath waitForConverter(OmniConverterFuture* future,
                              pxr::UsdStageRefPtr usdStage,
                              const std::string& meshStagePath,
                              const std::string& mesh_usd_path,
                              const std::string& meshPath,
                              const pxr::SdfPath& rootPath,
                              std::map<pxr::TfToken, pxr::SdfPath>& materialPaths)
{
    OmniConverterStatus status;

    // Wait for the converter to finish
    while (omniConverterCheckFutureStatus(future) == OmniConverterStatus::IN_PROGRESS)
    {
    }

    status = omniConverterCheckFutureStatus(future);
    omniConverterReleaseFuture(future);

    if (status == OmniConverterStatus::OK)
    {
        CARB_LOG_INFO("Asset %s convert successfully.", mesh_usd_path.c_str());
    }
    else
    {
        CARB_LOG_WARN(
            "Asset convert failed with error status: %s (%s)", StatusToString(status).c_str(), meshStagePath.c_str());
    }

    // Open the mesh stage and get the mesh prims
    pxr::UsdStageRefPtr meshStage = pxr::UsdStage::Open(mesh_usd_path);
    std::vector<pxr::UsdPrim> meshPrims{ meshStage->GetDefaultPrim() };

    // Create a base prim and move meshes and materials
    auto basePrim = pxr::UsdGeomXform::Define(usdStage, pxr::SdfPath(meshStagePath));
    for (const auto& mesh : meshPrims)
    {
        moveMeshAndMaterials(meshStage, usdStage, rootPath, mesh.GetPath(),
                             basePrim.GetPath().AppendChild(pxr::TfToken(mesh.GetName())), materialPaths);
    }

    // Clean up
    omniClientWait(omniClientDelete(mesh_usd_path.c_str(), {}, {}));
    pxr::UsdGeomImageable(usdStage->GetPrimAtPath(pxr::SdfPath(meshStagePath)))
        .CreateVisibilityAttr()
        .Set(pxr::UsdGeomTokens->inherited);

    return pxr::SdfPath(meshStagePath);
}


pxr::SdfPath SimpleImport(pxr::UsdStageRefPtr usdStage,
                          const std::string& path,
                          const std::string& meshPath,
                          std::map<pxr::TfToken, pxr::SdfPath>& meshList,
                          std::map<pxr::TfToken, pxr::SdfPath>& materialsList,
                          const pxr::SdfPath& rootPath)
{
    // Check if the mesh has already been imported
    pxr::SdfPath mesh_dst;
    if (meshList.count(pxr::TfToken(meshPath)))
    {
        // If it has, return the existing SdfPath
        mesh_dst = meshList[pxr::TfToken(meshPath)];
    }
    else
    {
        // Log a message indicating that we're importing a new mesh

        // Get the stage path and create a temporary USD file path
        std::string stage_path = usdStage->GetRootLayer()->GetIdentifier();
        std::string mesh_abs_path = resolve_path(meshPath);
        std::string mesh_usd_path = pathJoin(getParent(stage_path), getPathStem(meshPath.c_str()) + ".tmp.usd");

        CARB_LOG_INFO("Importing Mesh %s %s\n    (%s)", path.c_str(), meshPath.c_str(), mesh_abs_path.c_str());
        // Set up the Omni Converter flags
        int flags = OMNI_CONVERTER_FLAGS_SINGLE_MESH_FILE | OMNI_CONVERTER_FLAGS_IGNORE_CAMERAS |
                    OMNI_CONVERTER_FLAGS_USE_METER_PER_UNIT | OMNI_CONVERTER_FLAGS_MERGE_ALL_MESHES |
                    OMNI_CONVERTER_FLAGS_IGNORE_LIGHTS | OMNI_CONVERTER_FLAGS_FBX_CONVERT_TO_Z_UP |
                    OMNI_CONVERTER_FLAGS_IGNORE_PIVOTS | OMNI_CONVERTER_FLAGS_STAGE_UP_Z;

        // Set up the log and progress callbacks for the Omni Converter
        omniConverterSetLogCallback([](const char* message) { CARB_LOG_INFO("%s", message); });
        omniConverterSetProgressCallback([](OmniConverterFuture* future, uint32_t progress, uint32_t total)
                                         { CARB_LOG_INFO("Progress: %d / %d", progress, total); });

        // Create a new Omni Converter future for the mesh import
        auto future = omniConverterCreateAsset(mesh_abs_path.c_str(), mesh_usd_path.c_str(), flags);
        pxr::SdfPath next_path(isaacsim::asset::importer::urdf::GetNewSdfPathString(usdStage, path));
        mesh_dst = waitForConverter(
            future, usdStage, next_path.GetString(), mesh_usd_path, mesh_abs_path, rootPath, materialsList);

        // Add the new mesh to the mesh list
        meshList.emplace(pxr::TfToken(meshPath), mesh_dst);
    }

    return mesh_dst;
}
}
}
}
}
