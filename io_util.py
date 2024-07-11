import datetime
import os
import numpy as np
from sklearn.utils import shuffle


def get_outlier_threshold(path, z=1):
    len1 = _get_outlier_threshold(os.path.join(path, "Positive"), z)
    len2 = _get_outlier_threshold(os.path.join(path, "Negative"), z)
    if len1 > len2:
        return len1
    else:
        return len2


def _get_outlier_threshold(path, z):
    lengths = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.startswith("."):
                continue
            filepath = os.path.join(root, f)
            with open(filepath, "r", errors='ignore') as file:
                for line in file:
                    input_str = line.replace("\t", " ")
                    np_arr = np.fromstring(input_str, dtype=np.int32, sep=" ")
                    cur_width = len(np_arr)
                    lengths.append(cur_width)
    return compute_max(lengths, z=z)


def compute_max(arr, dim="width", z=2):
    mn = np.mean(arr, axis=0)
    sd = np.std(arr, axis=0)
    final_list = [x for x in arr if (x <= mn + z * sd)]  # upper outliers removed
    rmn2 = len(arr) - len(final_list)
    print('{} array size '.format(dim) + str(len(arr)))
    print('min {} '.format(dim) + str(min(arr)))
    print('max {} '.format(dim) + str(max(arr)))
    print('mean {} '.format(dim) + str(np.nanmean(arr)))
    print('standard deviation ' + str(np.std(arr)))
    print('median {} '.format(dim) + str(np.nanmedian(arr)))
    print('number of upper outliers removed ' + str(rmn2))
    print('max {} excluding upper outliers '.format(dim) + str(max(final_list)))
    return max(final_list)


def _retrieve_data(path, max_len):
    data = []
    for file in os.listdir(path):
        with open(os.path.join(path, file), 'r',
                  errors='ignore') as file_read:
            for line in file_read:
                input_str = line.replace("\t", " ")
                arr = np.fromstring(input_str, dtype=np.int32, sep=" ", count=max_len)
                arr_size = len(np.fromstring(input_str, dtype=np.int32, sep=" "))
                # We add this file only if the width is less than the outlier threshold
                if arr_size <= max_len:
                    arr[arr_size:max_len] = 0
                    data.append(arr)
    return data


def get_data_autoencoder(data_path, train_validate_ratio=0.7, max_training_samples=5000, max_eval_samples=150000):
    max_input_length = get_outlier_threshold(data_path, z=1)

    all_inputs = []
    # Positive cases
    folder_path = os.path.join(data_path, "Positive")
    pos_data_arr = _retrieve_data(folder_path, max_input_length)
    shuffle(pos_data_arr)
    total_positive_cases = len(pos_data_arr)

    # total_training_positive_cases = int(train_validate_ratio * total_positive_cases)
    total_eval_positive_cases = total_positive_cases

    # Negative cases
    folder_path = os.path.join(data_path, "Negative")
    neg_data_arr = _retrieve_data(folder_path, max_input_length)
    shuffle(neg_data_arr)
    total_negative_cases = len(neg_data_arr)

    total_training_negative_cases = int(train_validate_ratio * total_negative_cases)
    total_eval_negative_cases = int(total_negative_cases - total_training_negative_cases)

    # We balance training samples and apply max threshold for training sample count
    total_training_negative_cases = min(max_training_samples, total_training_negative_cases)

    training_data = []
    training_data.extend(neg_data_arr[0:total_training_negative_cases])
    training_data_arr = np.array(training_data, dtype=np.float32)

    # we need to remove extraneous samples from evaluation to keep the compuation in reasonable bounds
    if total_eval_negative_cases > max_eval_samples:
        removed_sample_percent = (total_eval_negative_cases - max_eval_samples) / total_eval_negative_cases
        total_eval_positive_cases = int(total_eval_positive_cases - total_eval_positive_cases * removed_sample_percent)
        total_eval_negative_cases = max_eval_samples

    eval_data = []
    eval_data.extend(pos_data_arr[len(pos_data_arr) - total_eval_positive_cases:])
    eval_data.extend(neg_data_arr[len(neg_data_arr) - total_eval_negative_cases:])
    eval_data_arr = np.array(eval_data, dtype=np.float32)

    eval_labels = np.empty(shape=[len(eval_data_arr)], dtype=np.float32)
    eval_labels[0:total_eval_positive_cases] = 1.0
    eval_labels[total_eval_positive_cases:] = 0.0

    training_data = training_data_arr.reshape((len(training_data_arr), max_input_length))
    eval_data = eval_data_arr.reshape((len(eval_labels), max_input_length))
    training_data = shuffle(training_data)
    eval_data, eval_labels = shuffle(eval_data, eval_labels)

    return training_data, eval_data, eval_labels, max_input_length


def write_result(file, str):
    f = open(file, "a+")
    f.write(str)
    f.close()


def get_out_file(out_folder, smell):
    now = datetime.datetime.now()
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    return os.path.join(out_folder, "ae_" + smell + "_"
                        + str(now.strftime("%d%m%Y_%H%M") + ".csv"))



def get_all_data(data_path, smell_name, train_validate_ratio):
    print("reading data...")
    max_eval_samples = 2000
    folder_path = os.path.join(data_path, smell_name, "1d")
    train_data, eval_data, eval_labels, max_input_length = \
        get_data_autoencoder(folder_path,
                                    train_validate_ratio=train_validate_ratio,
                                    max_training_samples=1000,
                                    max_eval_samples=max_eval_samples,
                                    )
    print("nan count: " + str(np.count_nonzero(np.isnan(train_data))))
    print("train_data: " + str(len(train_data)))
    print("train_data shape: " + str(train_data.shape))
    print("eval_data: " + str(len(eval_data)))
    print("eval_labels: " + str(len(eval_labels)))
    print("reading data... done.")
    return Input_data(train_data, None, eval_data, eval_labels, max_input_length)

class Input_data:
    def __init__(self, train_data, train_labels, eval_data, eval_labels, max_input_length):
        self.train_data = train_data
        self.train_labels = train_labels
        self.eval_data = eval_data
        self.eval_labels = eval_labels
        self.max_input_length = max_input_length