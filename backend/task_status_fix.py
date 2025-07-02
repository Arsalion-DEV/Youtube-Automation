# Fixed Task Status Management endpoints

@app.get("/api/tasks/status")
async def get_all_tasks_status():
    """Get status of all tasks"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT task_id, video_id, status, created_at, updated_at, progress, error_message
                FROM generation_tasks 
                ORDER BY created_at DESC 
                LIMIT 50
            """)
            
            tasks = []
            for row in cursor.fetchall():
                task_data = dict(row)
                tasks.append(task_data)
        
        return {
            "tasks": tasks,
            "total": len(tasks),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting all tasks status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """Get status of a specific task"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM generation_tasks WHERE task_id = ?
            """, (task_id,))
            
            row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task_data = dict(row)
        
        return {
            "task_id": task_id,
            "status": task_data.get("status", "unknown"),
            "progress": task_data.get("progress", 0),
            "video_id": task_data.get("video_id"),
            "created_at": task_data.get("created_at"),
            "updated_at": task_data.get("updated_at"),
            "error_message": task_data.get("error_message")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
