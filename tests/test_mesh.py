#!/usr/bin/env python3
# Author:  Octavio Castillo Reyes
# Contact: octavio.castillo@bsc.es

import pytest
import sys
import numpy as np
from petgem.mesh import readGmshNodes, readGmshConnectivity, computeEdges, computeFaces
from petgem.mesh import computeBoundaryFaces, computeBoundaryEdges, computeBoundaries
from petgem.mesh import readGmshPhysicalGroups
from petgem.vectors import invConnectivity
from petgem.hvfem import computeConnectivityDOFS

def test_mesh_functions():
    """Test mesh functions."""

    # Setup mesh file name
    mesh_filename = 'tests/data/test_mesh.msh'
    basis_order = 2
    # Read nodes
    nodes, _ = readGmshNodes(mesh_filename)

    # Read connectivity
    elemsN, nElems = readGmshConnectivity(mesh_filename)

    # Compute edges
    elemsE, edgesNodes = computeEdges(elemsN, nElems)
    nEdges = edgesNodes.shape[0]

    # Compute faces
    elemsF, facesN = computeFaces(elemsN, nElems)
    nFaces = facesN.shape[0]

    # Compute faces-edges connectivity
    N = invConnectivity(elemsF, nFaces)

    if nElems != 1:
        N = np.delete(N, 0, axis=1)

    # Allocate
    facesE = np.zeros((nFaces, 3), dtype=np.int)

    # Compute edges list for each face
    for i in np.arange(nFaces):
        iEle = N[i, 0]
        edgesEle = elemsE[iEle,:]
        facesEle = elemsF[iEle,:]
        kFace = np.where(facesEle == i)[0]
        if kFace == 0:  # Face 1
            facesE[facesEle[kFace],:] = [edgesEle[0], edgesEle[1], edgesEle[2]]
        elif kFace == 1:  # Face 2
            facesE[facesEle[kFace],:] = [edgesEle[0], edgesEle[4], edgesEle[3]]
        elif kFace == 2:  # Face 3
            facesE[facesEle[kFace],:] = [edgesEle[1], edgesEle[5], edgesEle[4]]
        elif kFace == 3:  # Face 4
            facesE[facesEle[kFace],:] = [edgesEle[2], edgesEle[5], edgesEle[3]]

    # Compute dofs connectivity

    # Compute degrees of freedom connectivity
    dofs, dof_edges, dof_faces, _, total_num_dofs = computeConnectivityDOFS(elemsE,elemsF,basis_order)

    # Compute boundary faces
    bFacesN, bFaces = computeBoundaryFaces(elemsF, facesN)

    # Compute boundary edges
    bEdges = computeBoundaryEdges(edgesNodes, bFacesN)

    # Verify mesh data
    assert nElems == 9453, "Wrong number of elements"
    assert nFaces == 20039, "Wrong number of faces"
    assert nEdges == 12748, "Wrong number of edges"
    assert total_num_dofs == 65574, "Wrong number of dofs"
