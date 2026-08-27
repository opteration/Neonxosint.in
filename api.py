from fastapi import FastAPI, Query, Request from fastapi.responses import HTMLResponse, JSONResponse from starlette.exceptions import HTTPException as StarletteHTTPException import duckdb
app = FastAPI()
con = duckdb.connect() con.execute("INSTALL httpfs;") con.execute("LOAD httpfs;")
LANDING_PAGE_HTML = """
const geometry = new THREE.BufferGeometry(); const vertices = []; for (let i = 0; i < 8000; i++) { vertices.push(THREE.MathUtils.randFloatSpread(3000)); vertices.push(THREE.MathUtils.randFloatSpread(3000)); vertices.push(THREE.MathUtils.randFloatSpread(3000)); } geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3)); const material = new THREE.PointsMaterial({ color: 0x00ffcc, size: 2.5, transparent: true, opacity: 0.8 }); const points = new THREE.Points(geometry, material); scene.add(points); camera.position.z = 1200;
function animate() { requestAnimationFrame(animate); points.rotation.x += 0.0005; points.rotation.y += 0.001; renderer.render(scene, camera); } animate();
window.addEventListener('resize', () => { camera.aspect = window.innerWidth / window.innerHeight; camera.updateProjectionMatrix(); renderer.setSize(window.innerWidth, window.innerHeight); }); </script>
@app.get("/", response_class=HTMLResponse) async def landing_page(): return LANDING_PAGE_HTML
@app.get("/search") async def search_number(number: str = Query(..., description="Phone number to search")): """ Search for a phone number in the Hitek database. Returns main records (mobile matching) and alternative records (alt matching). """ try: # Get last digit for sharding last_digit = number[-1] primary_url = f"https://huggingface.co/datasets/CuteHackX/hitek-data-bucket/resolve/main/final_master_shard_{last_digit}.parquet" alt_url = f"https://huggingface.co/datasets/CuteHackX/hitek-data-bucket/resolve/main/alt_master_shard_{last_digit}.parquet"
    # Query both main and alt tables
    query = f"""
    SELECT *, 'Main' AS _record_type FROM read_parquet('{primary_url}') WHERE mobile = '{number}'
    UNION ALL
    SELECT *, 'Alt' AS _record_type FROM read_parquet('{alt_url}') WHERE alt = '{number}'
    """
    
    raw_results = con.execute(query).df().to_dict(orient="records")
    
    # Separate main and alt records
    main_records = []
    alt_records = []
    
    for row in raw_results:
        rec_type = row.pop('_record_type')
        if rec_type == "Main":
            main_records.append(row)
        else:
            alt_records.append(row)
    
    if not main_records and not alt_records:
        return JSONResponse(
            status_code=404,
            content={
                "status": "not_found",
                "phone": number,
                "Developer": "@Maybechx"
            }
        )
    
    return {
        "status": "success",
        "Data": {
            "Main_Records": main_records,
            "Alt_Records": alt_records
        },
        "Developer": "@Maybechx"
    }
    
except Exception as e:
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": f"Database processing error: {str(e)}",
            "Developer": "@Maybechx"
        }
    )
@app.get("/health") async def health_check(): return {"status": "ok", "service": "Hitek Data Gateway"}
