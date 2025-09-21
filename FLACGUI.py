import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from mutagen.flac import FLAC

# Estilos visuales
BG_COLOR = "#121212"
FG_COLOR = "#FFFFFF"
ACCENT_COLOR = "#1DB954"

class FLACMetadataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FLAC Metadata Viewer")
        self.root.geometry("800x500")
        self.root.configure(bg=BG_COLOR)

        # Título
        self.label_title = tk.Label(root, text="FLAC Metadata Viewer", font=("Arial", 16, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR)
        self.label_title.pack(pady=10)

        # Botón para seleccionar carpeta
        self.btn_select = tk.Button(root, text="Seleccionar Carpeta", command=self.seleccionar_carpeta, bg=ACCENT_COLOR, fg="black", font=("Arial", 12, "bold"))
        self.btn_select.pack(pady=10)

        # Área de texto para mostrar el JSON
        self.text_area = tk.Text(root, wrap="word", height=20, bg="black", fg=FG_COLOR, insertbackground=FG_COLOR)
        self.text_area.pack(padx=10, pady=5, fill="both", expand=True)

        # Barra de desplazamiento
        self.scrollbar = ttk.Scrollbar(root, command=self.text_area.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=self.scrollbar.set)

        # Botón para copiar el JSON
        self.btn_copy = tk.Button(root, text="Copiar JSON", command=self.copiar_al_portapapeles, bg=ACCENT_COLOR, fg="black", font=("Arial", 12, "bold"))
        self.btn_copy.pack(pady=10)

    def seleccionar_carpeta(self):
        """Permite al usuario seleccionar una carpeta y extraer metadatos."""
        carpeta = filedialog.askdirectory(title="Selecciona una carpeta con archivos FLAC")
        if carpeta:
            self.extraer_metadatos_en_directorio(carpeta)

    def extraer_metadatos_en_directorio(self, directorio):
        """Procesa los archivos FLAC del directorio y muestra el JSON en el TextArea."""
        self.text_area.delete(1.0, tk.END)  # Limpiar área de texto

        if not os.path.exists(directorio):
            messagebox.showerror("Error", f"El directorio {directorio} no existe.")
            return

        archivos_flac = sorted(
            [archivo for archivo in os.listdir(directorio) if archivo.lower().endswith(".flac")],
            key=lambda x: (
                x.split('_')[0],  # Ordenar por la primera parte del nombre (descripción)
                int(x.split('_')[-1].split('.')[0])  # Ordenar por número de pista
            )
        )

        if not archivos_flac:
            messagebox.showinfo("Sin archivos", "No se encontraron archivos FLAC en la carpeta seleccionada.")
            return

        lista_metadatos = []
        for archivo in archivos_flac:
            ruta_completa = os.path.join(directorio, archivo)
            partes_nombre = os.path.splitext(archivo)[0].split('_')
            numero_descripcion = partes_nombre[0] if len(partes_nombre) >= 1 else "Desconocido"
            numero_pista = partes_nombre[-1] if len(partes_nombre) >= 2 else "0"
            total_archivos = sum(1 for archivo in archivos_flac if numero_descripcion in archivo)

            # Obtener metadatos
            metadatos = self.obtener_metadatos_flac(ruta_completa, numero_descripcion, numero_pista, total_archivos)
            if metadatos:
                lista_metadatos.append(metadatos)

        # Convertir a JSON y mostrar en el área de texto
        json_str = json.dumps(lista_metadatos, indent=4, ensure_ascii=False)
        self.text_area.insert(tk.END, json_str)

    def obtener_metadatos_flac(self, ruta_archivo, numero_descripcion, numero_pista, total_archivos):
        """Obtiene los metadatos de un archivo FLAC y los devuelve en formato JSON."""
        try:
            archivo_flac = FLAC(ruta_archivo)

            # Obtener metadatos con valores por defecto si faltan
            genero = archivo_flac.get("genre", ["Desconocido"])[0]
            titulo = archivo_flac.get("title", ["Sin título"])[0]
            artista = archivo_flac.get("artist", ["Desconocido"])[0]
            album = archivo_flac.get("album", ["Sin álbum"])[0]
            año = archivo_flac.get("YEAR", ["Desconocido"])[0][:4]  # Solo los primeros 4 caracteres del año

            return {
                "archivo_musica": os.path.join("Albums", os.path.basename(ruta_archivo)).replace("\\", "/"),
                "descripcion": numero_descripcion,
                "imagen": os.path.join("Albums", f"{numero_descripcion}.jpg").replace("\\", "/"),
                "genero": genero,
                "titulo": titulo,
                "artista": artista,
                "album": album,
                "numero_de_pista": f"{numero_pista}/{total_archivos}",
                "Año": año
            }

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron obtener metadatos de {ruta_archivo}: {e}")
            return None  # Si hay error, devolver None

    def copiar_al_portapapeles(self):
        """Copia el JSON generado al portapapeles."""
        json_text = self.text_area.get(1.0, tk.END).strip()
        if json_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(json_text)
            self.root.update()  # Necesario para que se copie correctamente
            messagebox.showinfo("Copiado", "El JSON ha sido copiado al portapapeles.")


# Inicializar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = FLACMetadataApp(root)
    root.mainloop()
