"""Clone directory/file structure of Obsidian notebooks related to SQL and database learning"""
import os, shutil
from typing import List 

class InvalidDirectoryError(ValueError):
    def __init__(self, dest: str) -> None:
        super().__init__(f"{dest} is not a valid directory")

class cloneObsidian:
    def __init__(self, folders: List[str]=None, files: List[str]=None, 
                dest: str=r"./Obsidian notebooks/",
                obsidian_path: str=None):
        
        if not os.path.isdir(dest):
            raise InvalidDirectoryError(dest)
            
        if not os.path.isdir(obsidian_path):
            raise InvalidDirectoryError(obsidian_path)
                
        self.dest = dest 
        self.obsidian_path = obsidian_path
        
        self.copyFiles(files)
        self.copyFolder(folders)
        
    def copyFiles(self, files: List[str]) -> int:
        """
        Copy files to destination
        Returns number of files copied
        """
        if files is None: return 
        
        src_path = self.obsidian_path + "{0}"
        dest_path = self.dest + "{0}"
        
        added = 0 
        for f in files:
            src_f = src_path.format(f)
            if not os.path.isfile(src_f):
                raise ValueError(f"{src_f} is not a valid file")
            
            dest_f = dest_path.format(f)
            if os.path.isfile(dest_f):
                print(f"{dest_f} already exists.")
                
            else:    
                shutil.copyfile( src_f, dest_f )
                print(f"Copied {f}")
                added += 1 
        
        print(f"Copied {added} files.")
        return added 
    
    def copyFolder(self, folders: List[str]):
        """Copy folders to destination"""
        if folders is None: return 
        
        added_files = 0 
        added_folders = 0 
        
        for folder in folders: 
            dest_f = self.dest + folder 
            
            if not os.path.isdir(dest_f): 
                os.mkdir(dest_f)
                added_folders += 1 
            
            files = [f"{folder}/{file}" for file in 
                    os.listdir(self.obsidian_path + folder)]
            
            if not files: continue 
            
            added_files += self.copyFiles(files)
            
        print(f"\nTotal added files: {added_files}")
        print(f"Total added folders: {added_folders}")
            
obsidian_path = r"C:/Users/delbe/Downloads/wut/wut/Post_grad/UBC/Research/records/obsidian notes/Literature/Computational/"
dest_path = r"./Obsidian notebooks/"
folders = ["Web Scraping - Mitchell"]
files = None

cloneObsidian(folders=folders, files=files, 
            obsidian_path=obsidian_path, 
            dest=dest_path)