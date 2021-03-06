#!/usr/bin/python3
import os
import sys
import json
from datetime import datetime
from dnode import datanode
import dnode

def update_namenode_logfile(logfile_path,dnode,block,operation,num_of_datanodes,namenode_path):
    with open(f'{logfile_path}',"a+") as logfile:
        if(operation=='put'):
            logfile.write(f"Datanode {dnode}'s Block {block} has been occupied, {datetime.now()} \n")
            for i in range(1,num_of_datanodes+1):
                with open(os.path.join(namenode_path , 'dnode_tracker.json')) as primary:
                    track_reader = json.loads(primary.read())
                    params = track_reader[str(i)]["count"]
                    logfile.write(f"Remaining Blocks in datanode {i} : {params} , {datetime.now()} \n")
                primary.close()
        if(operation=='rm'):
            logfile.write(f"Datanode {dnode}'s Block {block} has been removed, {datetime.now()} \n")
            for i in range(1,num_of_datanodes+1):
                with open(os.path.join(namenode_path , 'dnode_tracker.json')) as primary:
                    track_reader = json.loads(primary.read())
                    params = track_reader[str(i)]["count"]
                    logfile.write(f"Remaining Blocks in datanode {i} : {params} , {datetime.now()} \n")
                primary.close()
        if(operation=='cat'):
            logfile.write(f"Datanode {dnode}'s Block {block} content has been read and displayed, {datetime.now()} \n")
    logfile.close()

def mkdir(namenode_path,fs_path,directory_name):
    arrays = directory_name.split('/')
    path ='/'.join(arrays[:-1])
    intial_check = (fs_path + directory_name).split('.')
    if(len(intial_check)>=2):
        print("its not a directory")
        return
    if len(path)==0:
        check_path = fs_path + path
    else:
        check_path = fs_path + path + '/'
    directory_path = fs_path + directory_name + '/'
    global content
    with open(os.path.join(namenode_path , 'primary.json')) as primary:
        content = json.loads(primary.read())
        if(check_path not in content):
            print("Directory doesnt exist")
        elif(directory_path in content):
            print("Directory already exists")
        else:
            content[directory_path] = {}
        primary.close()
    with open(namenode_path+'primary.json', 'w') as primary:
        json.dump(content,primary)
        primary.close()


def cat(namenode_path,datanode_path,fs_path,file_path,namenode_logfile_path,datanode_logfile_path,num_of_datanodes,flag):
    extensions = file_path.split('.')[-1]
    name = file_path.split('/')[-1]
    check_path = fs_path + file_path
    global content_cat
    global json_reader
    json_reader = {}
    with open(os.path.join(namenode_path , 'primary.json')) as primary:
        content_cat = json.loads(primary.read())
        if(check_path not in content_cat):
            print("File not found")
        else:
            if(extensions=='json'):
                with open(os.path.join(namenode_path , 'hadoop_jobs.json') , "w") as reader:
                    json.dump(json_reader, reader)
                    reader.close()
            with open(os.path.join(namenode_path ,'hadoop_'+name),"w") as primary:
                    primary.write("")
                    primary.close()
            result = ""
            current_dict = content_cat[check_path]
            for i in range(1,len(current_dict)+1):
                empty_list = []
                
                for key,value in current_dict[str(i)].items():
                    empty_list.append((key,value))
                    break
                data_node = empty_list[0][0]
                data_node_block = empty_list[0][1]
                update_namenode_logfile(namenode_logfile_path,data_node,data_node_block,"cat",num_of_datanodes,namenode_path)
                dnode.update_datanode_logs(data_node,data_node_block,datanode_logfile_path,"cat")
                final_path = datanode_path + str(data_node) + '_data_node/' + str(data_node_block) + '.' + extensions
                if(extensions=='json'):
                    with open(final_path , 'r') as primary:
                        content = json.loads(primary.read())
                        json_reader.dump(content)
                        primary.close()
                else:
                    with open(final_path,"r") as file_read:
                        content_to_display = file_read.read()
                        with open(os.path.join(namenode_path ,'hadoop_'+name),"a") as primary:
                            primary.writelines(content_to_display)
                            primary.close()
                        if(flag==0):
                            print(content_to_display,end="")
                        file_read.close()
            print("\n")

def ls(namenode_path,fs_path,directory_path):
    check_path = fs_path + directory_path + '/'
    global content_ls
    with open(os.path.join(namenode_path , 'primary.json')) as primary:
        content_ls = json.loads(primary.read())
        if check_path not in content_ls:
            print("directory doesnt exist")
        else:
            check_path_splits = check_path.split('/')
            if(check_path_splits[-1] == ''):
                check_path_splits = check_path_splits[:-1]
            n = len(check_path_splits)
            result = []
            for key,value in content_ls.items():
                answer = key.split('/')
                if(answer[-1] == ''):
                    answer = answer[:-1]
                if(answer[:n]==check_path_splits and len(answer)>n):
                    result.append(answer[n])
            if(len(result)==0):
                print("nothing exists in this directory")
            else:
                for i in result:
                    print(i)


def rm(namenode_path,datanode_path,fs_path,file_path,dnode_logfile_path,namenode_logfile_path,num_datanodes):
    check_path = fs_path + file_path
    extensions = file_path.split('.')[-1]
    global content_rm
    global content_tracker
    with open(os.path.join(namenode_path , 'dnode_tracker.json')) as tracks:
        content_tracker = json.loads(tracks.read())
        tracks.close()
    with open(os.path.join(namenode_path , 'primary.json')) as primary:
        content_rm = json.loads(primary.read())
        if check_path not in content_rm:
            print("File does not exist")
        else:
            file_dict = content_rm[check_path]
            n = len(file_dict)
            for i in range(1,n+1):
                empty_list = []
                cur_dict = file_dict[str(i)]
                for key,value in file_dict[str(i)].items():
                    empty_list.append((key,value))
                for k in empty_list:
                    dnode_number = k[0]
                    dnode_block = k[1]
                    content_tracker[str(dnode_number)][str(dnode_block)] = 0
                    content_tracker[str(dnode_number)]["count"] += 1
                    dnode.update_datanode_logs(dnode_number,dnode_block,dnode_logfile_path,'rm')
                    update_namenode_logfile(namenode_logfile_path,dnode_number,dnode_block,'rm',num_datanodes,namenode_path)
                    with open(namenode_path+'dnode_tracker.json', 'w') as trackers:
                        json.dump(content_tracker,trackers)
                        trackers.close() 
                    del_path = datanode_path + str(dnode_number) + "_data_node/" + str(dnode_block) + '.' + extensions
                    os.remove(del_path)
            content_rm.pop(check_path)
            with open(namenode_path+'primary.json', 'w') as primary_of:
                json.dump(content_rm,primary_of)
                primary_of.close()
            with open(namenode_path+'dnode_tracker.json', 'w') as trackers:
                json.dump(content_tracker,trackers)
                trackers.close()
    primary.close()



def rmdir(namenode_path,datanode_path,fs_path,directory_path):
    check_path = fs_path + directory_path + '/'
    global content_rmdir
    with open(os.path.join(namenode_path , 'primary.json')) as primary:
        content_rmdir = json.loads(primary.read())
        primary.close()
    if check_path not in content_rmdir:
        print("Directory doesnt exist")
    else:
        fspath_len=len(fs_path.split('/')[:-1])
        check_path_splits = check_path.split('/')
        if(check_path_splits[-1] == ''):
            check_path_splits = check_path_splits[:-1]
        n = len(check_path_splits)
        file = []
        folder = []

        for key,value in content_rmdir.items():
            answer = key.split('/')
            if(answer[-1] == ''):
                answer = answer[:-1]
            if(answer[:n]==check_path_splits and len(answer)>=n):
                if len(answer[-1].split('.'))>1:
                    path_file=answer[fspath_len:]
                    path_file='/'.join(path_file)
                    file.append(path_file)
                else:
                    folder.append(key)
        if(len(file)>0):
            for item in file:
                rm(namenode_path,datanode_path,fs_path,item)
        global read_content
        with open(os.path.join(namenode_path , 'primary.json')) as primary:
            read_content = json.loads(primary.read())
            primary.close()
        if(len(folder)>0):
            for item in folder:
                read_content.pop(item)
        with open(namenode_path+'primary.json', 'w') as primary_of:
            json.dump(read_content,primary_of)
            primary_of.close()
                        
                        
            



                


            
    



                




        
        
        


        






        