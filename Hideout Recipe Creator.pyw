
import os
import json
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from rapidfuzz import process, fuzz
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rapidfuzz"])
    from rapidfuzz import process, fuzz

BASE = os.getcwd()

ITEMS_PATH = os.path.join(BASE,"SPT","SPT_Data","database","templates","items.json")
LOCALE_PATH = os.path.join(BASE,"SPT","SPT_Data","database","locales","global","en.json")

AREA_TYPES={
"Vents":0,"Security":1,"Lavatory":2,"Generator":4,"Heating":5,"Water Collector":6,
"Med Station":7,"Nutrition Unit":8,"Rest Space":9,"Workbench":10,
"Intelligence Center":11,"Shooting Range":12,"Library":13,"Scav Case":14,
"Illumination":15,"Hall Of Fame":16,"Air Filtering Unit":17,"Solar Power":18,
"Booze Generator":19,"Bitcoin Farm":20,"Christmas Tree":21,"Gym":23,
"Weapon Stand":24,"Weapon Stand Secondary":25,"Equipment Presets Stand":26,"Cult Circle":27
}

with open(ITEMS_PATH,encoding="utf-8") as f:
    ITEMS=json.load(f)

with open(LOCALE_PATH,encoding="utf-8") as f:
    LOCALE=json.load(f)

name_to_id={}
id_to_name={}
ITEM_NAMES=[]

for k,v in LOCALE.items():
    if k.endswith(" Name"):
        iid=k.replace(" Name","")
        if iid in ITEMS:
            name=v.replace('"',"")
            name_to_id[name]=iid
            id_to_name[iid]=name
            ITEM_NAMES.append(name)

def search_items(text):
    text=text.lower().strip()
    if not text:
        return []
    prefix=[]
    substring=[]
    for name in ITEM_NAMES:
        low=name.lower()
        if low.startswith(text):
            prefix.append(name)
            continue
        if text in low:
            substring.append(name)
    if prefix:
        return prefix[:10]
    if substring:
        return substring[:10]
    results=process.extract(text,ITEM_NAMES,limit=10,scorer=fuzz.WRatio)
    return [r[0] for r in results if r[1] > 80]

def find_item(name):
    if name in name_to_id:
        return name_to_id[name]
    res=process.extractOne(name,ITEM_NAMES,scorer=fuzz.WRatio)
    if res and res[1] > 85:
        return name_to_id[res[0]]
    return None

def mark_invalid(widget):
    widget.config(bg="#ffcccc")

def mark_valid(widget):
    widget.config(bg="white")

ingredients=[]
tools=[]
error_label=None

def set_error(msg):
    if error_label:
        error_label.config(text=msg)

def validate_fields():
    valid=True
    error=None

    if not recipe_id.get().strip():
        mark_invalid(recipe_id)
        error="Recipe ID cannot be empty"
        valid=False
    else:
        mark_valid(recipe_id)

    if required_level.get_int() is None:
        mark_invalid(required_level)
        error=error or "Required Level must be a positive integer"
        valid=False
    else:
        mark_valid(required_level)

    if production_time.get_int() is None:
        mark_invalid(production_time)
        error=error or "Production Time must be > 0"
        valid=False
    else:
        mark_valid(production_time)

    if output_count.get_int() is None:
        mark_invalid(output_count)
        error=error or "Output Count must be > 0"
        valid=False
    else:
        mark_valid(output_count)

    if not find_item(end_product.get()):
        mark_invalid(end_product.entry)
        error=error or "End Product is not a valid item"
        valid=False
    else:
        mark_valid(end_product.entry)

    for name_field,count_field,row in ingredients:
        if not find_item(name_field.get()):
            mark_invalid(name_field.entry)
            error=error or "Ingredient contains invalid item"
            valid=False
        else:
            mark_valid(name_field.entry)

        if count_field.get_int() is None:
            mark_invalid(count_field)
            error=error or "Ingredient count must be > 0"
            valid=False
        else:
            mark_valid(count_field)

    for name_field,count_field,row in tools:
        if not find_item(name_field.get()):
            mark_invalid(name_field.entry)
            error=error or "Tool contains invalid item"
            valid=False
        else:
            mark_valid(name_field.entry)

        if count_field.get_int() is None:
            mark_invalid(count_field)
            error=error or "Tool count must be > 0"
            valid=False
        else:
            mark_valid(count_field)

    set_error("" if valid else error)
    return valid

class AutocompleteEntry(tk.Frame):

    def __init__(self,master,width=25):
        super().__init__(master)
        self.var=tk.StringVar()
        self.entry=tk.Entry(self,textvariable=self.var,width=width)
        self.entry.pack(fill="x",expand=True)
        self.entry.bind("<KeyRelease>",self.changed)
        self.var.trace_add("write",lambda *a: validate_fields())
        self.popup=None
        self.listbox=None

    def changed(self,event=None):
        text=self.var.get()
        matches=search_items(text)
        if not matches:
            self.close()
            return
        if not self.popup:
            self.popup=tk.Toplevel(root)
            self.popup.wm_overrideredirect(True)
            self.listbox=tk.Listbox(self.popup,height=6)
            self.listbox.pack(fill="both",expand=True)
            self.listbox.bind("<ButtonRelease-1>",self.select)
        self.listbox.delete(0,tk.END)
        for m in matches:
            self.listbox.insert(tk.END,m)
        self.position()

    def position(self):
        if not self.popup:
            return
        x=self.entry.winfo_rootx()
        y=self.entry.winfo_rooty()+self.entry.winfo_height()
        self.popup.geometry(f"{self.entry.winfo_width()}x120+{x}+{y}")
        self.popup.lift()

    def select(self,event):
        idx=self.listbox.curselection()
        if not idx:
            return
        value=self.listbox.get(idx)
        self.entry.delete(0,tk.END)
        self.entry.insert(0,value)
        self.close()
        validate_fields()

    def close(self):
        if self.popup:
            self.popup.destroy()
            self.popup=None
            self.listbox=None

    def get(self):
        return self.entry.get()

class IntEntry(tk.Entry):

    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.bind("<KeyRelease>",lambda e: validate_fields())

    def get_int(self):
        v=self.get().strip()
        if not v.isdigit():
            return None
        n=int(v)
        if n<=0:
            return None
        return n

root=tk.Tk()
root.title("SPT Recipe Generator")
root.geometry("920x880")

main=tk.Frame(root)
main.pack(fill="both",expand=True)

def labeled(label,widget):
    frame=tk.Frame(main)
    frame.pack(fill="x")
    tk.Label(frame,text=label,width=25,anchor="w").pack(side="left")
    field=widget(frame)
    field.pack(side="left",fill="x",expand=True)
    return field

recipe_id=labeled("Recipe ID",tk.Entry)
recipe_id.bind("<KeyRelease>",lambda e: validate_fields())

required_level=labeled("Required Level",IntEntry)
production_time=labeled("Production Time",IntEntry)
end_product=labeled("End Product",AutocompleteEntry)
output_count=labeled("Output Count",IntEntry)

fuel_var=tk.BooleanVar()
tk.Checkbutton(main,text="Requires Fuel",variable=fuel_var).pack(anchor="w")

tk.Label(main,text="Hideout Area").pack(anchor="w")
area_dropdown=ttk.Combobox(main,values=list(AREA_TYPES.keys()),state="readonly")
area_dropdown.pack(fill="x")

ingredient_frame=tk.LabelFrame(main,text="Ingredients")
ingredient_frame.pack(fill="x",pady=10)

def remove_ing(row):
    row.destroy()
    ingredients[:] = [x for x in ingredients if x[2]!=row]
    validate_fields()

def add_ingredient():
    row=tk.Frame(ingredient_frame)
    row.pack(fill="x")

    name_field=AutocompleteEntry(row)
    name_field.pack(side="left",fill="x",expand=True)

    count_field=IntEntry(row,width=6)
    count_field.pack(side="left")

    tk.Button(row,text="Remove",command=lambda:remove_ing(row)).pack(side="right")

    ingredients.append((name_field,count_field,row))
    validate_fields()

tk.Button(ingredient_frame,text="Add Ingredient",command=add_ingredient).pack(fill="x")
add_ingredient()

tools_var=tk.BooleanVar()

def toggle_tools():
    if tools_var.get():
        tools_frame.pack(fill="x",pady=10)
    else:
        tools_frame.pack_forget()

tools_frame=tk.LabelFrame(main,text="Tools")


def remove_tool(row):
    row.destroy()
    tools[:] = [x for x in tools if x[2] != row]
    validate_fields()

def add_tool():
    row=tk.Frame(tools_frame)
    row.pack(fill="x")

    name_field=AutocompleteEntry(row)
    name_field.pack(side="left",fill="x",expand=True)

    count_field=IntEntry(row,width=6)
    count_field.pack(side="left")

    
    tk.Button(row,text="Remove",command=lambda:remove_tool(row)).pack(side="right")
    tools.append((name_field,count_field,row))

    validate_fields()

tk.Checkbutton(main,text="Use Tools",variable=tools_var,command=toggle_tools).pack(anchor="w")
tk.Button(tools_frame,text="Add Tool",command=add_tool).pack(fill="x")

def load_recipe_data(data):

    recipe_id.delete(0,tk.END)
    recipe_id.insert(0,data.get("_id",""))

    required_level.delete(0,tk.END)
    required_level.insert(0,data.get("requiredLevel",""))

    production_time.delete(0,tk.END)
    production_time.insert(0,data.get("productionTime",""))

    output_count.delete(0,tk.END)
    output_count.insert(0,data.get("count",""))

    fuel_var.set(data.get("needFuelForAllProductionTime",False))

    for name,val in AREA_TYPES.items():
        if val==data.get("areaType"):
            area_dropdown.set(name)

    ep=data.get("endProduct")
    if ep in id_to_name:
        end_product.entry.delete(0,tk.END)
        end_product.entry.insert(0,id_to_name[ep])

    for name,count,row in ingredients:
        row.destroy()
    ingredients.clear()

    for inp in data.get("inputs",[]):
        add_ingredient()
        f,c,row=ingredients[-1]
        f.entry.delete(0,tk.END)
        f.entry.insert(0,id_to_name.get(inp["tpl"],""))
        c.delete(0,tk.END)
        c.insert(0,inp["count"])

    # Clear existing tools
    for name,count,row in tools:
        row.destroy()
    tools.clear()

    if data.get("tools"):
        tools_var.set(True)
        tools_frame.pack(fill="x",pady=10)

        for t in data["tools"]:
            add_tool()
            f,c,row = tools[-1]

            f.entry.delete(0,tk.END)
            f.entry.insert(0, id_to_name.get(t.get("tpl"), ""))

            c.delete(0,tk.END)
            c.insert(0, t.get("count", ""))
    else:
        tools_var.set(False)

    validate_fields()

def import_from_file():
    path=filedialog.askopenfilename(filetypes=[("JSON","*.json")])
    if not path:
        return
    with open(path,"r",encoding="utf-8") as f:
        data=json.load(f)
    load_recipe_data(data)

def import_from_text():

    win=tk.Toplevel(root)
    win.title("Paste JSON")
    win.geometry("600x500")

    txt=tk.Text(win)
    txt.pack(fill="both",expand=True)

    def do_import():
        try:
            data=json.loads(txt.get("1.0","end"))
            load_recipe_data(data)
            win.destroy()
        except Exception as e:
            messagebox.showerror("Invalid JSON",str(e))

    tk.Button(win,text="Import",command=do_import).pack(pady=5)

output=tk.Text(root,height=14)
output.pack(fill="both")

button_bar=tk.Frame(root)
button_bar.pack(pady=8)

import_btn=tk.Menubutton(button_bar,text="Import JSON",relief="raised")
menu=tk.Menu(import_btn,tearoff=0)
menu.add_command(label="Import from file",command=import_from_file)
menu.add_command(label="Import from text",command=import_from_text)
import_btn.config(menu=menu)
import_btn.pack(side="left",padx=5)

def generate():
    if not validate_fields():
        messagebox.showerror("Validation Error","Fix highlighted fields.")
        return

    rid=recipe_id.get().strip()
    lvl=required_level.get_int()
    prod=production_time.get_int()
    cnt=output_count.get_int()
    area=area_dropdown.get()
    end=find_item(end_product.get())

    inputs=[]
    for n,c,row in ingredients:
        inputs.append({"tpl":find_item(n.get()),"count":c.get_int()})

    recipe={
        "_id":rid,
        "areaType":AREA_TYPES[area],
        "requiredLevel":lvl,
        "productionTime":prod,
        "endProduct":end,
        "count":cnt,
        "needFuelForAllProductionTime":fuel_var.get(),
        "inputs":inputs
    }

    output.delete("1.0",tk.END)
    output.insert(tk.END,json.dumps(recipe,indent=2))

tk.Button(button_bar,text="Generate Recipe",command=generate).pack(side="left",padx=5)

error_label=tk.Label(root,text="",fg="red")
error_label.pack()

root.mainloop()
