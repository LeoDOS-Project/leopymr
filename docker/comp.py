#! /usr/bin/env python3
import glob
import importlib
from utils import log

class CompFinder:
  def __init__(self):
    self.map_tasks = {}
    self.reduce_tasks = {}
    self.collect_tasks = {}
    self.combine_tasks = {}
  def find_map(self, map_name):
    return self.map_tasks.get(map_name)
  def register_map(self, map_name, map_task):
    self.map_tasks[map_name] = map_task
  def find_reduce(self, reduce_name):
    return self.reduce_tasks.get(reduce_name)
  def register_reduce(self, reduce_name, reduce_task):
    self.reduce_tasks[reduce_name] = reduce_task
  def find_collect(self, collect_name):
    return self.collect_tasks.get(collect_name)
  def register_collect(self, collect_name, collect_task):
    self.collect_tasks[collect_name] = collect_task
  def find_combine(self, combine_name):
    return self.combine_tasks.get(combine_name)
  def register_combine(self, combine_name, combine_task):
    self.combine_tasks[combine_name] = combine_task
  def register(self, task_type, task_name, task):
    log(f"registering {task_type} name {task_name} task {task}",verbosity=2)
    if task_type == "mappers":
      self.register_map(task_name, task)
    elif task_type == "reducers":
      self.register_reduce(task_name, task)
    elif task_type == "collectors":
      self.register_collect(task_name, task)
    elif task_type == "combiners":
      self.register_combine(task_name, task)

comp_finder = CompFinder()

task_files = {}
task_files["mappers"] = glob.glob("mappers/*.py")
task_files["reducers"] = glob.glob("reducers/*.py")
task_files["collectors"] = glob.glob("collectors/*.py")
task_files["combiners"] = glob.glob("combiners/*.py")

for task_type in task_files.keys():
  for file_name in task_files[task_type]:
    module_name = file_name.replace(".py","").split("/")[1]
    dynamic_module = importlib.import_module(f"{task_type}.{module_name}")
    comp_finder.register(task_type,module_name,dynamic_module.get_task())
  


