# Mermaid ERD Usage Guide
## Quick Start Instructions

## 📁 Files Created

1. **`ERD_MERMAID.md`** - Full documentation with Mermaid code and instructions
2. **`ERD_MERMAID_SIMPLIFIED.md`** - Simplified version (easier to render)
3. **`database_erd.mmd`** - Standalone Mermaid file (copy-paste ready)
4. **`MERMAID_USAGE_GUIDE.md`** - This guide

---

## 🚀 Quick Start (3 Steps)

### Step 1: Copy the Mermaid Code
- Open `database_erd.mmd` or `ERD_MERMAID.md`
- Copy the entire Mermaid code block (everything between ```mermaid and ```)

### Step 2: Go to Mermaid Live Editor
- Visit: **https://mermaid.live/**
- Paste the code in the editor
- The diagram will render automatically

### Step 3: Export and Use
- Click **"Actions"** → **"Download PNG"** (or SVG/PDF)
- Insert the image into your Google Doc
- Done! ✅

---

## 🎯 Method 1: Mermaid Live Editor (Recommended)

**Best for:** Quick export to image

1. **Go to:** https://mermaid.live/
2. **Paste** the Mermaid code from `database_erd.mmd`
3. **View** the rendered diagram
4. **Export:**
   - Click "Actions" → "Download PNG" (for Google Doc)
   - Or "Download SVG" (for scalable vector)
   - Or "Download PDF" (for printing)

**Pros:**
- ✅ Free, no account needed
- ✅ Instant rendering
- ✅ Multiple export formats
- ✅ Easy to use

---

## 🎯 Method 2: GitHub/GitLab (Best for Sharing)

**Best for:** Sharing with team/mentor via repository

1. **Create a file:** `ERD.md` in your repository
2. **Add the Mermaid code:**
   ```markdown
   # Database ERD
   
   ```mermaid
   erDiagram
       User {
           uuid id PK
           ...
       }
       ...
   ```
   ```
3. **Commit and push**
4. **View on GitHub/GitLab** - It renders automatically!
5. **Share the link** with your mentor

**Pros:**
- ✅ Version controlled
- ✅ Automatic rendering
- ✅ Easy to share
- ✅ No export needed

---

## 🎯 Method 3: VS Code (Best for Editing)

**Best for:** Editing and previewing locally

1. **Install extension:**
   - "Markdown Preview Mermaid Support" by Matt Bierner
2. **Open** `ERD_MERMAID.md` in VS Code
3. **Preview:** Press `Ctrl+Shift+V` (or `Cmd+Shift+V` on Mac)
4. **Export:** Right-click preview → "Save as HTML" or screenshot

**Pros:**
- ✅ Edit and preview in one place
- ✅ No internet needed
- ✅ Full control

---

## 🎯 Method 4: Notion (Best for Documentation)

**Best for:** Including in comprehensive documentation

1. **Open Notion**
2. **Create a new page**
3. **Type:** `/mermaid` and select "Mermaid"
4. **Paste** the Mermaid code
5. **Share** the Notion page

**Pros:**
- ✅ Native Mermaid support
- ✅ Great for documentation
- ✅ Easy collaboration

---

## 🎯 Method 5: Google Docs (Direct Integration)

**Best for:** Final submission

### Option A: Export from Mermaid Live
1. Go to https://mermaid.live/
2. Paste code and render
3. Export as PNG
4. Insert into Google Doc: **Insert → Image → Upload**

### Option B: Use Mermaid Add-on
1. Open Google Doc
2. **Add-ons** → **Get add-ons** → Search "Mermaid"
3. Install a Mermaid add-on (if available)
4. Or use the image method (Option A)

**Recommended:** Use Option A (export as PNG and insert)

---

## 📊 Which Version to Use?

### Use Full Version (`database_erd.mmd`) if:
- ✅ You need all 35 entities
- ✅ You want complete documentation
- ✅ The diagram renders fine in your tool

### Use Simplified Version (`ERD_MERMAID_SIMPLIFIED.md`) if:
- ✅ The full diagram is too large/complex
- ✅ You want to focus on core relationships
- ✅ You're having rendering issues

---

## 🔧 Troubleshooting

### Problem: Diagram doesn't render
**Solutions:**
1. Check Mermaid syntax (ensure proper indentation)
2. Try the simplified version
3. Use Mermaid Live Editor (most reliable)
4. Check for syntax errors in the code

### Problem: Diagram is too large/cluttered
**Solutions:**
1. Use the simplified version
2. Split into multiple diagrams (one per entity group)
3. Zoom out in the viewer
4. Export as SVG and scale down

### Problem: Relationships are hard to see
**Solutions:**
1. Use Mermaid Live Editor's zoom feature
2. Export as SVG (scalable)
3. Use different relationship styles
4. Split into multiple focused diagrams

### Problem: Attributes are cut off
**Solutions:**
1. Reduce number of attributes shown
2. Use abbreviated field names
3. Focus on key attributes only
4. Use the simplified version

---

## 📝 Customization Tips

### Show Only Key Attributes
Edit the Mermaid code to show only essential fields:
```mermaid
User {
    uuid id PK
    string username UK
    string email
    string role
}
```

### Change Relationship Labels
Modify relationship labels for clarity:
```mermaid
User ||--o{ Job : "posts_as_employer"
User ||--o{ Application : "applies_as_applicant"
```

### Add Colors (Advanced)
Mermaid supports styling (in some contexts):
```mermaid
classDef userClass fill:#e1f5ff
class User userClass
```

---

## ✅ Submission Checklist

- [ ] Mermaid code copied from `database_erd.mmd`
- [ ] Diagram rendered successfully
- [ ] Exported as PNG/SVG
- [ ] Image inserted into Google Doc
- [ ] Google Doc sharing permissions set
- [ ] Diagram is clear and readable
- [ ] All key entities visible
- [ ] Relationships are clear

---

## 🎨 Export Settings Recommendations

### For Google Doc:
- **Format:** PNG
- **Resolution:** 300 DPI (if available)
- **Size:** Large enough to read clearly

### For Print:
- **Format:** PDF or SVG
- **Resolution:** 300 DPI minimum
- **Size:** Full page or larger

### For Web:
- **Format:** SVG (scalable) or PNG
- **Resolution:** 150-200 DPI
- **Size:** Optimized for web

---

## 🔗 Useful Links

- **Mermaid Live Editor:** https://mermaid.live/
- **Mermaid Documentation:** https://mermaid.js.org/
- **Mermaid ERD Syntax:** https://mermaid.js.org/syntax/entityRelationshipDiagram.html
- **Mermaid.ink (API):** https://mermaid.ink/ (for programmatic rendering)

---

## 💡 Pro Tips

1. **Start with simplified version** - Test rendering first
2. **Use Mermaid Live Editor** - Most reliable rendering
3. **Export as PNG for Google Doc** - Best compatibility
4. **Keep a backup** - Save the `.mmd` file
5. **Version control** - Commit Mermaid files to Git

---

## 📚 Additional Resources

- See `DATABASE_ERD_DOCUMENTATION.md` for detailed entity information
- See `ERD_QUICK_REFERENCE.md` for quick entity reference
- See `ERD_SUBMISSION_GUIDE.md` for submission instructions

---

**Ready to create your ERD? Start with Step 1 above! 🚀**
