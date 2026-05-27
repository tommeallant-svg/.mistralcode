"""
API routes for dataset operations.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from typing import Optional, List, Dict, Any
from fastapi.responses import JSONResponse

from ..models.dataset import DatasetCreateRequest, DatasetQueryRequest
from ..schemas.dataset import (
    DatasetResponse,
    DatasetListResponse,
    DatasetCreateResponse,
    DatasetQueryResponse,
    ErrorResponse
)
from ..services.dataset_service import DatasetService
from ..config import settings

router = APIRouter(prefix="/api/v1/datasets", tags=["datasets"])


def get_dataset_service():
    """Dependency for getting dataset service"""
    return DatasetService()


@router.get("/", response_model=DatasetListResponse, summary="List all datasets")
async def list_datasets(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of datasets"),
    offset: int = Query(default=0, ge=0, description="Number of datasets to skip"),
    service: DatasetService = Depends(get_dataset_service)
):
    """List all available datasets"""
    await service.initialize()
    try:
        response = await service.list_datasets(limit=limit, offset=offset)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.post("/", response_model=DatasetCreateResponse, summary="Create a new dataset")
async def create_dataset(
    request: DatasetCreateRequest,
    service: DatasetService = Depends(get_dataset_service)
):
    """Create a new dataset from a CSV file or existing source"""
    await service.initialize()
    try:
        response = await service.create_dataset(request)
        return DatasetCreateResponse(
            success=True,
            dataset=response,
            message="Dataset created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await service.shutdown()


@router.get("/{name}", response_model=DatasetResponse, summary="Get dataset details")
async def get_dataset(
    name: str,
    service: DatasetService = Depends(get_dataset_service)
):
    """Get details of a specific dataset"""
    await service.initialize()
    try:
        dataset = await service.get_dataset(name)
        if dataset:
            return dataset
        raise HTTPException(status_code=404, detail=f"Dataset '{name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.delete("/{name}", summary="Delete a dataset")
async def delete_dataset(
    name: str,
    service: DatasetService = Depends(get_dataset_service)
):
    """Delete a dataset by name"""
    await service.initialize()
    try:
        success = await service.delete_dataset(name)
        if success:
            return JSONResponse(content={"success": True, "message": f"Dataset '{name}' deleted"})
        raise HTTPException(status_code=404, detail=f"Dataset '{name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.shutdown()


@router.post("/{name}/upload", summary="Upload CSV file to create dataset")
async def upload_csv_dataset(
    name: str,
    file: UploadFile = File(...),
    description: Optional[str] = Query(default=None, description="Dataset description"),
    service: DatasetService = Depends(get_dataset_service)
):
    """Upload a CSV file to create or update a dataset"""
    await service.initialize()
    try:
        # Create request with file
        request = DatasetCreateRequest(
            name=name,
            description=description,
            file=file
        )
        
        response = await service.create_dataset(request)
        return DatasetCreateResponse(
            success=True,
            dataset=response,
            message=f"CSV file uploaded and dataset '{name}' created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await service.shutdown()


@router.post("/{name}/query", response_model=DatasetQueryResponse, summary="Query dataset data")
async def query_dataset(
    name: str,
    request: DatasetQueryRequest,
    service: DatasetService = Depends(get_dataset_service)
):
    """Query data from a specific dataset"""
    await service.initialize()
    try:
        request.dataset_name = name
        response = await service.query_dataset(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        await service.shutdown()


@router.get("/{name}/columns", summary="Get dataset columns")
async def get_dataset_columns(
    name: str,
    service: DatasetService = Depends(get_dataset_service)
):
    """Get column information for a dataset"""
    await service.initialize()
    try:
        columns = await service.get_dataset_columns(name)
        return JSONResponse(content={
            "dataset_name": name,
            "columns": columns
        })
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    finally:
        await service.shutdown()


@router.get("/{name}/stats", summary="Get dataset statistics")
async def get_dataset_stats(
    name: str,
    service: DatasetService = Depends(get_dataset_service)
):
    """Get statistics for a dataset"""
    await service.initialize()
    try:
        stats = await service.get_dataset_stats(name)
        return JSONResponse(content={
            "dataset_name": name,
            "stats": stats
        })
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    finally:
        await service.shutdown()
