#!/usr/bin/python3
import os
import sys
import json
from datetime import datetime


files_json = {}
datanode = {}


def hashing(file_block_no, num_of_datanodes):
    hashed_value = file_block_no % num_of_datanodes
    if(datanode[hashed_value+1] > 0):
        return hashed_value+1
    else:
        j = 1
        while(datanode[j] == 0 and j < num_of_datanodes):
            j = j+1
        if(j<num_of_datanodes):
            return j
        elif(datanode[j]==0):
            return -1
        else:
            return -1


def create_datanode(num_datanodes, datanode_size, Datanode_path):
    for dnode in range(1, num_datanodes+1):
        os.makedirs(Datanode_path+str(dnode)+"_data_node")
        datanode[dnode] = datanode_size
	

def create_namenode(Namenode_path):
	os.makedirs(Namenode_path)
	primary_json = {}
	with open(Namenode_path+'primary.json', 'w') as primary:
		json.dump(primary_json, primary)

def create_logfiles(logfile_path,num_datanodes):
    os.mkdir(logfile_path)
    for dnode in range(1, num_datanodes+1):
        with open(f'{logfile_path}{dnode}_datanode_log.txt',"w+") as logfile:
            logfile.write(f"Datanode {dnode} has been created, {datetime.now()}\n")
        logfile.close()


def update_logs(dnode,block,dnode_logfile_path,operation):
    with open(f'{dnode_logfile_path}{dnode}_datanode_log.txt',"a+") as logfile:
        if(operation=='put'):
            logfile.write(f"Block {block} has been occupied, {datetime.now()} \n")


def initial_split(filename,block_size,datanode_size,num_datanodes,path_datanode,Namenode_path,logfile_path):
        with open(filename, 'rb') as bytefile:
            ext = filename.split('.')[1]
            block_size = block_size * 1024 * 1024
            files_json[filename]={}
            content = bytearray(os.path.getsize(filename))
            bytefile.readinto(content)
            file_splits=len(content)/block_size
            available_blocks=0
            for key,value in datanode.items():
                available_blocks+=value
            if(available_blocks<file_splits):
                print('Less blocks available')
                return
            for file_block, i in enumerate(range(0, len(content), block_size)):
                files_json[filename][file_block+1] = {}
                hash_value = hashing(file_block, num_datanodes)
                if(hash_value == -1):
                    print('No space to insert file block')
                    return
                dnode_block = datanode_size-datanode[hash_value]+1
                with open(f'{path_datanode}{hash_value}'+'_data_node/' + str(dnode_block) + '.'+ext, 'wb') as fh:
                    files_json[str(filename)][file_block +
                                          1][hash_value] = dnode_block
                    datanode[hash_value] -= 1
                    fh.write(content[i: i + block_size])
                    update_logs(hash_value,dnode_block,logfile_path,'put')
                fh.close()
            bytefile.close()
        with open(Namenode_path+'primary.json', 'w') as primary:
            json.dump(files_json, primary)


def replicate_files(filename,block_size,datanode_size,num_datanodes,path_datanode,Namenode_path,replication_factor,logfile_path):
    remaining_blocks = 0
    ext = filename.split('.')[1]
    block_size = block_size * 1024 * 1024
    for key,value in datanode.items():
        remaining_blocks += value
    with open(filename, 'rb') as bytefile:
        content = bytearray(os.path.getsize(filename))
        bytefile.readinto(content)
        file_splits=len(content)/block_size
        can_replicate = min(replication_factor-1,int(remaining_blocks/file_splits))
        if(can_replicate<1):
            print('No Space to replicate')
            return
    bytefile.close()
    for file_block, i in enumerate(range(0, len(content), block_size)):
        hash_value = hashing(file_block,num_datanodes)
        current_block=files_json[str(filename)][file_block+1][hash_value]
        with open(f'{path_datanode}/{hash_value}' + '_data_node/' + str(current_block) + '.'+ext, 'rb') as bytefile:
            for file_block_replica in range(1,can_replicate+1):
                next_dnode=((hash_value-1+file_block_replica)%num_datanodes)+1
                next_dnode_block = datanode_size-datanode[next_dnode]+1
                with open(f'{path_datanode}/{next_dnode}' + '_data_node/' + str(next_dnode_block) + '.'+ext, 'wb') as fh:
                    files_json[str(filename)][file_block+1][next_dnode]=next_dnode_block
                    datanode[next_dnode]-=1
                    fh.write(content[i: i + block_size])
                    update_logs(next_dnode,next_dnode_block,logfile_path,'put')
                fh.close()
        bytefile.close()
    with open(Namenode_path+'primary.json', 'w') as primary:
            json.dump(files_json, primary)
    
    




            



