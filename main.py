import json
import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from ollama import AsyncClient
import base64

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "running"}


@app.post("/recommend")
async def recommend(
    image: UploadFile = File(...),
    style: str = Form(...),
    occasion: str = Form(...)
):
    """
    Get clothing recommendations based on uploaded image, style, and occasion.
    Uses Ollama's llava model for vision understanding.
    """
    temp_file_path = None
    try:
        # Save uploaded image to temp file
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, image.filename)
        
        with open(temp_file_path, "wb") as f:
            contents = await image.read()
            f.write(contents)
        
        # Read image and encode to base64
        with open(temp_file_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        step1_user = """You are a luxury fashion stylist analyzing an image.

STEP 1 - IMAGE ANALYSIS (REQUIRED):
First, examine the image very carefully and describe EXACTLY what you see:
- The specific clothing item(s) or outfit visible
- Exact colors and any patterns, textures, or materials visible
- Formality level (casual, business, formal, etc.)
- Any visible details like fit, style elements, or accessories

Be very specific about ONLY what you can literally see. Do not make assumptions.

Return your response in this exact format:
IMAGE ANALYSIS: [Your detailed description of what you see in the image]"""

        step3_user = f"""STEP 2 - COMPLEMENTARY RECOMMENDATIONS:
look at the item you described in your previous response and identify its category — for example if it is a shirt, top, blouse, or any upper body garment then do not recommend any other upper body garments. If it is trousers, jeans, skirt, or any lower body garment then do not recommend any other lower body garments. If it is a dress or jumpsuit that covers the whole body then focus recommendations on accessories, shoes, outerwear, and bags only. If it is a shoe or sandal then do not recommend other shoes. If it is a bag then do not recommend other bags. The 5 recommendations must span at least 3 distinct categories — for example a mix of bottoms, shoes, outerwear, accessories, and bags — so the user gets a complete outfit suggestion rather than redundant alternatives for the same item they already have.

Based ONLY on the specific item you just described, provide exactly 5 clothing recommendations that directly complement it.

CRITICAL REQUIREMENTS FOR DESCRIPTIONS:
- Each of the 5 recommendations must have a DISTINCT description written from a different stylist's perspective:
  * Description 1: Focus on COLOR THEORY — explain why the color tones complement each other
  * Description 2: Focus on SILHOUETTE & PROPORTION — how it balances the proportions of the item from the image
  * Description 3: Focus on TEXTURE & FABRIC — contrast or fabric pairing details
  * Description 4: Focus on CULTURAL/STYLISTIC CONTEXT — cultural significance or style movement relevance
  * Description 5: Focus on OCCASION APPROPRIATENESS — how it works for the specific occasion
- Do NOT start any two descriptions with the same word
- Use "pairs well" at most once across all 5 descriptions
- Each description must be 1 to 2 sentences only
- Write as if each was written by a different stylist with a unique perspective

IMPORTANT: Do NOT provide generic recommendations. Every item must specifically coordinate with the clothing in the image in terms of:
- Color harmony (complementary or matching colors)
- Formality level (must match the formality of the item in the image)
- Overall style

Style preference: {style}
Occasion: {occasion}

Return your response in this exact format:
RECOMMENDATIONS: [A plain JSON array with no markdown, backticks, or extra text. Start with [ and end with ]. Each object must have: type, name, description (explain how it complements the item from the image), colors (array of strings), color_hex (array of hex codes), tags (array of 3 strings)]"""

        client = AsyncClient(timeout=120.0)
        first = await client.chat(
            model="llava",
            messages=[
                {
                    "role": "user",
                    "content": step1_user,
                    "images": [image_data],
                }
            ],
            options={"temperature": 0.3},
        )
        analysis_text = first.message.content
        generated_text = (
            await client.chat(
                model="llava",
                messages=[
                    {
                        "role": "user",
                        "content": step1_user,
                        "images": [image_data],
                    },
                    {"role": "assistant", "content": analysis_text},
                    {"role": "user", "content": step3_user},
                ],
                options={"temperature": 0.3},
            )
        ).message.content
        
        # Extract JSON from response
        try:
            # Find the RECOMMENDATIONS section
            if "RECOMMENDATIONS:" in generated_text:
                rec_start = generated_text.find("RECOMMENDATIONS:")
                json_part = generated_text[rec_start + len("RECOMMENDATIONS:"):].strip()
            else:
                json_part = generated_text.strip()
            
            # Try to find JSON array in the response
            start_idx = json_part.find("[")
            end_idx = json_part.rfind("]") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = json_part[start_idx:end_idx]
                recommendations = json.loads(json_str)
            else:
                recommendations = json.loads(json_part)
        except json.JSONDecodeError:
            # If parsing fails, return error response
            return {
                "error": "Failed to parse recommendations",
                "recommendations": []
            }
        
        return {"recommendations": recommendations}
    
    except Exception as e:
        return {
            "error": str(e),
            "recommendations": []
        }
    
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
