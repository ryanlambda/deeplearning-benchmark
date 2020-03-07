import os
import re
import pandas as pd


path_result = 'results'

#list_system = ['2xV100'] 
list_system = ['2xV100', 'V100', 'QuadroRTX8000', 'QuadroRTX6000', 'QuadroRTX5000', 'TitanRTX', '2080Ti', '1080Ti'] 

list_test = {
             'PyTorch_SSD_FP32': ('PyTorch_SSD_FP32 (images/sec)', "^.*Training performance =.*$", -2),
             'PyTorch_SSD_AMP': ('PyTorch_SSD_AMP (images/sec)', "^.*Training performance =.*$", -2),
             'PyTorch_resnet50_FP32': ('PyTorch_resnet50_FP32 (images/sec)', "^.*Summary: train.loss.*$", -2),
             'PyTorch_resnet50_FP16': ('PyTorch_resnet50_FP16 (images/sec)', "^.*Summary: train.loss.*$", -2),
             'PyTorch_resnet50_AMP': ('PyTorch_resnet50_AMP (images/sec)', "^.*Summary: train.loss.*$", -2),
             'PyTorch_maskrcnn_FP32': ('PyTorch_maskrcnn_FP32 (images/sec)', "^.*Training perf is:.*$", -2),
             'PyTorch_maskrcnn_FP16': ('PyTorch_maskrcnn_FP16 (images/sec)', "^.*Training perf is:.*$", -2),
             'PyTorch_gnmt_FP32': ('PyTorch_gnmt_FP32 (tokens/sec)', "^.*Training:.*$", -4),
             'PyTorch_gnmt_FP16': ('PyTorch_gnmt_FP16 (tokens/sec)', "^.*Training:.*$", -4),
             'PyTorch_ncf_FP32': ('PyTorch_ncf_FP32 (samples/sec)', "^.*best_train_throughput:.*$", -1),
             'PyTorch_ncf_FP16': ('PyTorch_ncf_FP16 (samples/sec)', "^.*best_train_throughput:.*$", -1),
             'PyTorch_transformerxlbase_FP32': ('PyTorch_transformerxlbase_FP32 (tokens/sec)', "^.*Training throughput:.*$", -2),
             'PyTorch_transformerxlbase_FP16': ('PyTorch_transformerxlbase_FP16 (tokens/sec)', "^.*Training throughput:.*$", -2),
             'PyTorch_transformerxllarge_FP32': ('PyTorch_transformerxllarge_FP32 (tokens/sec)', "^.*Training throughput:.*$", -2),
             'PyTorch_transformerxllarge_FP16': ('PyTorch_transformerxllarge_FP16 (tokens/sec)', "^.*Training throughput:.*$", -2),
             'PyTorch_tacotron2_FP32': ('PyTorch_tacotron2_FP32 (samples/sec)', "^.*train_epoch_avg_items/sec:.*$", -1),
             'PyTorch_tacotron2_FP16': ('PyTorch_tacotron2_FP16 (samples/sec)', "^.*train_epoch_avg_items/sec:.*$", -1),
             'PyTorch_waveglow_FP32': ('PyTorch_waveglow_FP32 (samples/sec)', "^.*train_epoch_avg_items/sec:.*$", -1),
             'PyTorch_waveglow_FP16': ('PyTorch_waveglow_FP16 (samples/sec)', "^.*train_epoch_avg_items/sec:.*$", -1),
             'PyTorch_bert_large_squad_FP32': ('PyTorch_bert_large_squad_FP32 (sequences/sec)', "^.*training throughput:.*$", -1),
             'PyTorch_bert_large_squad_FP16': ('PyTorch_bert_large_squad_FP16 (sequences/sec)', "^.*training throughput:.*$", -1),
             'PyTorch_bert_base_squad_FP32': ('PyTorch_bert_base_squad_FP32 (sequences/sec)', "^.*training throughput:.*$", -1),
             'PyTorch_bert_base_squad_FP16': ('PyTorch_bert_base_squad_FP16 (sequences/sec)', "^.*training throughput:.*$", -1),
             }


def gather_avg(name, system, df):
    
    column_name, key, pos = list_test[name]
    pattern = re.compile(key)

    path = path_result + '/' + system + '/' + name
    count = 0.000001
    total_throughput = 0.0

    for filename in os.listdir(path):
        if filename.endswith(".txt"):
            flag = False
            for i, line in enumerate(open(os.path.join(path, filename))):

                for match in re.finditer(pattern, line):

                    try:
                        throughput = float(match.group().split(' ')[pos])
                        
                        if throughput > 0:
                            count += 1
                            total_throughput += throughput
                            flag = True
                        else:
                            pass

                    except:
                        pass

            if not flag:
                print(system + "/" + name + " " + filename + ": something wrong")
                    

    df.at[system, column_name] = round(total_throughput / count, 2)


def gather_last(name, system, df):
    
    column_name, key, pos = list_test[name]
    pattern = re.compile(key)

    path = path_result + '/' + system + '/' + name
    count = 0.000001
    total_throughput = 0.0

    for filename in os.listdir(path):
        if filename.endswith(".txt"):
            flag = False
            throughput = 0
            # Sift through all lines and only keep the last occurrence
            for i, line in enumerate(open(os.path.join(path, filename))):

                for match in re.finditer(pattern, line):

                    try:
                        throughput = float(match.group().split(' ')[pos])
                    except:
                        pass

            if throughput > 0:
                count += 1
                total_throughput += throughput
                flag = True

            if not flag:
                print(system + "/" + name + " " + filename + ": something wrong")
                    

    df.at[system, column_name] = round(total_throughput / count, 2)
def main():

    columns = []
    for test_name, value in sorted(list_test.iteritems()):
        columns.append(list_test[test_name][0])


    df = pd.DataFrame(index=list_system, columns=columns)
    df = df.fillna(-1.0)

    for system in list_system:
        for test_name, value in sorted(list_test.iteritems()):
            gather_last(test_name, system, df)


    df.to_csv('pytorch.csv')

if __name__ == "__main__":
    main()

