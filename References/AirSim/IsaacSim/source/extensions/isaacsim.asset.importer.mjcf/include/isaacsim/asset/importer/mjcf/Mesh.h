// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#pragma once
// clang-format off
#include <pch/UsdPCH.h>
// clang-format on

#include <isaacsim/core/includes/math/core/Core.h>
#include <isaacsim/core/includes/math/core/Maths.h>

#include <omniverse_asset_converter.h>
#include <string>
#include <vector>

/**
 * @struct TextureData
 * @brief Container for texture image data and metadata.
 * @details
 * This structure holds texture information including dimensions, pixel data,
 * and format. Can represent both compressed and uncompressed texture data.
 */
struct TextureData
{
    /** @brief Width of texture in pixels. If height is 0, width equals buffer size. */
    int width; // width of texture - if height == 0, then width will be the same
               // as buffer.size()

    /** @brief Height of texture in pixels. If 0, buffer contains compressed image data. */
    int height; // height of textur - if height == 0, then the buffer represents a
                // compressed image with file type corresponding to format

    /** @brief Pixel data buffer. R8G8B8A8 format if uncompressed. */
    std::vector<uint8_t> buffer; // r8g8b8a8 if not compressed

    /** @brief Format string for compressed data (e.g., "png", "jpg", "bmp"). */
    std::string format; // format of the data in buffer if compressed (i.e. png, jpg, bmp)
};

/**
 * @struct Material
 * @brief OBJ-style material definition with PBR properties.
 * @details
 * Direct representation of .obj style material with ambient, diffuse,
 * specular components and modern PBR extensions for metallic workflow.
 */
struct Material
{
    /** @brief Name identifier for the material. */
    std::string name;

    /** @brief Ambient color component (RGB). */
    Vec3 Ka;

    /** @brief Diffuse color component (RGB). */
    Vec3 Kd;

    /** @brief Specular color component (RGB). */
    Vec3 Ks;

    /** @brief Emissive color component (RGB). */
    Vec3 emissive;

    /** @brief Specular exponent for shininess calculation. */
    float Ns = 50.0f; // specular exponent

    /** @brief Metallic factor for PBR rendering (0.0 = dielectric, 1.0 = metallic). */
    float metallic = 0.0f;

    /** @brief Specular reflectance factor. */
    float specular = 0.0f;

    /** @brief Diffuse texture map file path. */
    std::string mapKd = ""; // diffuse

    /** @brief Specular/shininess texture map file path. */
    std::string mapKs = ""; // shininess

    /** @brief Normal/bump texture map file path. */
    std::string mapBump = ""; // normal

    /** @brief Environment/emissive texture map file path. */
    std::string mapEnv = ""; // emissive

    /** @brief Metallic texture map file path. */
    std::string mapMetallic = "";

    /** @brief Whether the material has a diffuse texture. */
    bool hasDiffuse = false;

    /** @brief Whether the material has a specular texture. */
    bool hasSpecular = false;

    /** @brief Whether the material has a metallic texture. */
    bool hasMetallic = false;

    /** @brief Whether the material has an emissive texture. */
    bool hasEmissive = false;

    /** @brief Whether the material has a shininess texture. */
    bool hasShininess = false;
};

/**
 * @struct MaterialAssignment
 * @brief Defines which triangles and indices use a specific material.
 * @details
 * This structure maps ranges of triangles and vertex indices to a specific
 * material, allowing meshes to have multiple materials across different regions.
 */
struct MaterialAssignment
{
    /** @brief Starting triangle index for this material assignment. */
    int startTri;

    /** @brief Ending triangle index for this material assignment. */
    int endTri;

    /** @brief Starting vertex index for this material assignment. */
    int startIndices;

    /** @brief Ending vertex index for this material assignment. */
    int endIndices;

    /** @brief Index of the material to use for this range. */
    int material;
};

/**
 * @struct UVInfo
 * @brief UV texture coordinate information for mesh surfaces.
 * @details
 * Contains UV mapping data with support for multiple UV sets and
 * corresponding index arrays for texture coordinate assignment.
 */
struct UVInfo
{
    /** @brief UV coordinate arrays for multiple texture sets. */
    std::vector<std::vector<Vector2>> uvs;

    /** @brief Starting indices for UV coordinate arrays. */
    std::vector<unsigned int> uvStartIndices;
};

/**
 * @enum GymMeshNormalMode
 * @brief Defines how mesh normals should be computed or loaded.
 * @details
 * Used when loading meshes to determine the strategy for handling
 * surface normal vectors for lighting calculations.
 */
enum GymMeshNormalMode
{
    /** @brief Load normals from the mesh asset if available. */
    eFromAsset, // try to load normals from the mesh

    /** @brief Compute smooth per-vertex normals. */
    eComputePerVertex, // compute per-vertex normals

    /** @brief Compute flat per-face normals. */
    eComputePerFace, // compute per-face normals
};

/**
 * @struct USDMesh
 * @brief USD-compatible mesh data structure.
 * @details
 * Contains mesh geometry data formatted for USD (Universal Scene Description)
 * with support for points, faces, normals, UVs, and colors.
 */
struct USDMesh
{
    /** @brief Name identifier for the USD mesh. */
    std::string name;

    /** @brief Array of 3D vertex positions. */
    pxr::VtArray<pxr::GfVec3f> points;

    /** @brief Number of vertices per face (typically 3 for triangles). */
    pxr::VtArray<int> faceVertexCounts;

    /** @brief Vertex indices defining face connectivity. */
    pxr::VtArray<int> faceVertexIndices;

    /** @brief Face-varying normal vectors for lighting. */
    pxr::VtArray<pxr::GfVec3f> normals; // Face varing normals

    /** @brief Face-varying UV texture coordinates. */
    pxr::VtArray<pxr::VtArray<pxr::GfVec2f>> uvs; // Face varing uvs

    /** @brief Face-varying vertex colors. */
    pxr::VtArray<pxr::VtArray<pxr::GfVec3f>> colors; // Face varing colors
};

/**
 * @struct Mesh
 * @brief Core mesh data structure with geometry and material information.
 * @details
 * Contains vertex data, connectivity information, materials, and various
 * utility functions for mesh manipulation and processing. Supports conversion
 * to USD format and asset conversion operations.
 */
struct Mesh
{
    /**
     * @brief Merges another mesh into this mesh.
     * @details
     * Combines vertex data, indices, and materials from the source mesh
     * into this mesh, effectively creating a single merged mesh.
     *
     * @param[in] m The mesh to merge into this mesh
     */
    void AddMesh(const Mesh& m);

    /**
     * @brief Gets the total number of vertices in the mesh.
     * @return Number of vertices as unsigned 32-bit integer
     */
    uint32_t GetNumVertices() const
    {
        return uint32_t(m_positions.size());
    }

    /**
     * @brief Gets the total number of faces (triangles) in the mesh.
     * @return Number of faces as unsigned 32-bit integer
     */
    uint32_t GetNumFaces() const
    {
        return uint32_t(m_indices.size()) / 3;
    }

    /**
     * @brief Duplicates a vertex at the specified index.
     * @details
     * Creates a copy of the vertex data at the given index, adding it
     * to the end of the vertex arrays.
     *
     * @param[in] i Index of the vertex to duplicate
     */
    void DuplicateVertex(uint32_t i);

    /**
     * @brief Calculates face normals by splitting vertices.
     * @details
     * Computes faceted normals by duplicating vertices where needed,
     * changing the mesh topology to create sharp edges between faces.
     */
    void CalculateFaceNormals(); // splits mesh at vertices to calculate faceted
                                 // normals (changes topology)

    /**
     * @brief Calculates smooth vertex normals.
     * @details
     * Computes per-vertex normals by averaging adjacent face normals,
     * creating smooth shading across the surface.
     */
    void CalculateNormals();

    /**
     * @brief Transforms the mesh by the given transformation matrix.
     * @details
     * Applies the transformation matrix to all vertex positions and
     * normal vectors in the mesh.
     *
     * @param[in] m 4x4 transformation matrix to apply
     */
    void Transform(const Matrix44& m);

    /**
     * @brief Normalizes the mesh to fit within specified bounds.
     * @details
     * Scales the mesh so that its maximum dimension equals the specified
     * size and moves it so the minimum bound is at origin.
     *
     * @param[in] s Target size for the largest dimension (default: 1.0)
     */
    void Normalize(float s = 1.0f); // scale so bounds in any dimension equals s
                                    // and lower bound = (0,0,0)

    /**
     * @brief Flips the mesh by reversing face winding order.
     * @details
     * Reverses the vertex order of all triangles, effectively flipping
     * the surface normals and changing inside/outside orientation.
     */
    void Flip();

    /**
     * @brief Calculates the axis-aligned bounding box of the mesh.
     * @details
     * Computes the minimum and maximum extents of the mesh along
     * each coordinate axis.
     *
     * @param[out] minExtents Minimum bounds of the mesh
     * @param[out] maxExtents Maximum bounds of the mesh
     */
    void GetBounds(Vector3& minExtents, Vector3& maxExtents) const;

    /** @brief Optional name identifier for the mesh. */
    std::string name; // optional

    /** @brief Array of vertex positions in 3D space. */
    std::vector<Point3> m_positions;

    /** @brief Array of vertex normal vectors. */
    std::vector<Vector3> m_normals;

    /** @brief Array of 2D texture coordinates per vertex. */
    std::vector<Vector2> m_texcoords;

    /** @brief Array of vertex colors. */
    std::vector<Colour> m_colours;

    /** @brief Array of vertex indices defining triangle connectivity. */
    std::vector<uint32_t> m_indices;

    /** @brief Array of materials used by this mesh. */
    std::vector<Material> m_materials;

    /** @brief Array of material assignments to mesh regions. */
    std::vector<MaterialAssignment> m_materialAssignments;

    /** @brief Array of USD-compatible mesh representations. */
    std::vector<USDMesh> m_usdMeshPrims;

    /** @brief Path to converted USD mesh file. */
    std::string m_convertedUsdMesh;

    /** @brief Scale factor applied to the mesh (X, Y, Z). */
    Vec3 scale = { 1.0f, 1.0f, 1.0f };

    /** @brief Pointer to asset conversion status tracker. */
    OmniConverterFuture* m_assetConvertStatus = nullptr;
};


/**
 * @brief Exports a mesh to binary format.
 * @details
 * Saves mesh data in a flat binary format for efficient storage and loading.
 *
 * @param[in] path File path where the binary mesh data will be saved
 * @param[in] m Pointer to the mesh to export
 */
void ExportMeshToBin(const char* path, const Mesh* m);

/**
 * @brief Creates a triangular mesh primitive.
 * @details
 * Generates a simple triangle mesh with the specified size.
 *
 * @param[in] size Size of the triangle
 * @param[in] y Y-coordinate offset (default: 0.0)
 * @return Pointer to the created triangle mesh
 */
Mesh* CreateTriMesh(float size, float y = 0.0f);

/**
 * @brief Creates a cube mesh primitive.
 * @details
 * Generates a unit cube mesh with 6 faces and proper normals.
 *
 * @return Pointer to the created cube mesh
 */
Mesh* CreateCubeMesh();

/**
 * @brief Creates a subdivided quad mesh.
 * @details
 * Generates a rectangular mesh divided into a grid of smaller quads.
 *
 * @param[in] sizex Width of the quad in the X direction
 * @param[in] sizez Height of the quad in the Z direction
 * @param[in] gridx Number of subdivisions along X axis
 * @param[in] gridz Number of subdivisions along Z axis
 * @return Pointer to the created quad mesh
 */
Mesh* CreateQuadMesh(float sizex, float sizez, int gridx, int gridz);

/**
 * @brief Creates a circular disc mesh.
 * @details
 * Generates a flat circular mesh with the specified radius and number of segments.
 *
 * @param[in] radius Radius of the disc
 * @param[in] segments Number of radial segments for tessellation
 * @return Pointer to the created disc mesh
 */
Mesh* CreateDiscMesh(float radius, uint32_t segments);

/**
 * @brief Creates a tetrahedron mesh primitive.
 * @details
 * Generates a tetrahedral mesh with specified ground level and height.
 *
 * @param[in] ground Ground level Y-coordinate (default: 0.0)
 * @param[in] height Height of the tetrahedron (default: 1.0)
 * @return Pointer to the created tetrahedron mesh
 */
Mesh* CreateTetrahedron(float ground = 0.0f,
                        float height = 1.0f); // fixed but not used

/**
 * @brief Creates a sphere mesh primitive.
 * @details
 * Generates a spherical mesh using latitude and longitude tessellation.
 *
 * @param[in] slices Number of longitudinal slices
 * @param[in] segments Number of latitudinal segments
 * @param[in] radius Radius of the sphere (default: 1.0)
 * @return Pointer to the created sphere mesh
 */
Mesh* CreateSphere(int slices, int segments, float radius = 1.0f);

/**
 * @brief Creates an ellipsoid mesh primitive.
 * @details
 * Generates an ellipsoidal mesh with different radii along each axis.
 *
 * @param[in] slices Number of longitudinal slices
 * @param[in] segments Number of latitudinal segments
 * @param[in] radiis Radii along X, Y, and Z axes
 * @return Pointer to the created ellipsoid mesh
 */
Mesh* CreateEllipsoid(int slices, int segments, Vec3 radiis);

/**
 * @brief Creates a capsule mesh primitive.
 * @details
 * Generates a capsule (cylinder with hemispherical end caps) mesh.
 *
 * @param[in] slices Number of circumferential slices
 * @param[in] segments Number of segments along the length
 * @param[in] radius Radius of the capsule (default: 1.0)
 * @param[in] halfHeight Half-height of the cylindrical portion (default: 1.0)
 * @return Pointer to the created capsule mesh
 */
Mesh* CreateCapsule(int slices, int segments, float radius = 1.0f, float halfHeight = 1.0f);

/**
 * @brief Creates a cylinder mesh primitive.
 * @details
 * Generates a cylindrical mesh with optional end caps.
 *
 * @param[in] slices Number of circumferential slices
 * @param[in] radius Radius of the cylinder
 * @param[in] halfHeight Half-height of the cylinder
 * @param[in] cap Whether to include end caps (default: false)
 * @return Pointer to the created cylinder mesh
 */
Mesh* CreateCylinder(int slices, float radius, float halfHeight, bool cap = false);
