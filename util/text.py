import numpy as np
import tensorflow as tf
import re

# Constants
SPACE_TOKEN = '<space>'
SPACE_INDEX = 0
FIRST_INDEX = ord('a') - 1  # 0 is reserved to space

def text_to_char_array(original):
    # Create list of sentence's words w/spaces replaced by ''
    result = original.replace(" '", "") # TODO: Deal with this properly
    result = result.replace("'", "")    # TODO: Deal with this properly
    result = result.replace(' ', '  ')
    result = result.split(' ')

    # Tokenize words into letters adding in SPACE_TOKEN where required
    result = np.hstack([SPACE_TOKEN if xt == '' else list(xt) for xt in result])

    # Map characters into indicies
    result = np.asarray([SPACE_INDEX if xt == SPACE_TOKEN else ord(xt) - FIRST_INDEX for xt in result])

    # Add result to results
    return result

def sparse_tuple_from(sequences, dtype=np.int32):
    """Create a sparse representention of x.
    Args:
        sequences: a list of lists of type dtype where each element is a sequence
    Returns:
        A tuple with (indices, values, shape)
    """
    indices = []
    values = []

    for n, seq in enumerate(sequences):
        indices.extend(zip([n]*len(seq), xrange(len(seq))))
        values.extend(seq)

    indices = np.asarray(indices, dtype=np.int64)
    values = np.asarray(values, dtype=dtype)
    shape = np.asarray([len(sequences), indices.max(0)[1]+1], dtype=np.int64)

    return tf.SparseTensor(indices=indices, values=values, shape=shape)

def sparse_tensor_value_to_texts(value):
    return sparse_tuple_to_texts((value.indices, value.values, value.shape))

def sparse_tuple_to_texts(tuple):
    indices = tuple[0]
    values = tuple[1]
    results = [''] * tuple[2][0]
    for i in range(len(indices)):
        index = indices[i][0]
        c = values[i]
        c = ' ' if c == SPACE_INDEX else chr(c + FIRST_INDEX)
        results[index] = results[index] + c
    # List of strings
    return results

def ndarray_to_text(value):
    results = ''
    for i in range(len(value)):
        results += chr(value[i] + FIRST_INDEX)
    return results.replace('`', ' ')

def wer(original, result):
    """
    The WER is defined as the editing/Levenshtein distance on word level
    divided by the amount of words in the original text.
    In case of the original having more words (N) than the result and both
    being totally different (all N words resulting in 1 edit operation each),
    the WER will always be 1 (N / N = 1).
    """
    # The WER ist calculated on word (and NOT on character) level.
    # Therefore we split the strings into words first:
    original = original.split()
    result = result.split()
    return levenshtein(original, result) / float(len(original))

def wers(originals, results):
    count = len(originals)
    rates = []
    mean = 0.0
    assert count == len(results)
    for i in range(count):
        rate = wer(originals[i], results[i])
        mean = mean + rate
        rates.append(rate)
    return rates, mean / float(count)

# The following code is from: http://hetland.org/coding/python/levenshtein.py

# This is a straightforward implementation of a well-known algorithm, and thus
# probably shouldn't be covered by copyright to begin with. But in case it is,
# the author (Magnus Lie Hetland) has, to the extent possible under law,
# dedicated all copyright and related and neighboring rights to this software
# to the public domain worldwide, by distributing it under the CC0 license,
# version 1.0. This software is distributed without any warranty. For more
# information, see <http://creativecommons.org/publicdomain/zero/1.0>

def levenshtein(a,b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n

    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]

# gather_nd is taken from https://github.com/tensorflow/tensorflow/issues/206#issuecomment-229678962
# 
# Unfortunately we can't just use tf.gather_nd because it does not have gradients
# implemented yet, so we need this workaround.
#
def gather_nd(params, indices, shape):
    rank = len(shape)
    flat_params = tf.reshape(params, [-1])
    multipliers = [reduce(lambda x, y: x*y, shape[i+1:], 1) for i in range(0, rank)]
    indices_unpacked = tf.unpack(tf.transpose(indices, [rank - 1] + range(0, rank - 1)))
    flat_indices = sum([a*b for a,b in zip(multipliers, indices_unpacked)])
    return tf.gather(flat_params, flat_indices)

# ctc_label_dense_to_sparse is taken from https://github.com/tensorflow/tensorflow/issues/1742#issuecomment-205291527
#
# The CTC implementation in TensorFlow needs labels in a sparse representation,
# but sparse data and queues don't mix well, so we store padded tensors in the
# queue and convert to a sparse representation after dequeuing a batch.
#
def ctc_label_dense_to_sparse(labels, label_lengths, batch_size):
    # The second dimension of labels must be equal to the longest label length in the batch
    correct_shape_assert = tf.assert_equal(tf.shape(labels)[1], tf.reduce_max(label_lengths))
    with tf.control_dependencies([correct_shape_assert]):
        labels = tf.identity(labels)

    label_shape = tf.shape(labels)
    num_batches_tns = tf.pack([label_shape[0]])
    max_num_labels_tns = tf.pack([label_shape[1]])
    def range_less_than(previous_state, current_input):
        return tf.expand_dims(tf.range(label_shape[1]), 0) < current_input

    init = tf.cast(tf.fill(max_num_labels_tns, 0), tf.bool)
    init = tf.expand_dims(init, 0)
    dense_mask = tf.scan(range_less_than, label_lengths, initializer=init, parallel_iterations=1)
    dense_mask = dense_mask[:, 0, :]

    label_array = tf.reshape(tf.tile(tf.range(0, label_shape[1]), num_batches_tns),
          label_shape)
    label_ind = tf.boolean_mask(label_array, dense_mask)

    batch_array = tf.transpose(tf.reshape(tf.tile(tf.range(0, label_shape[0]), max_num_labels_tns), tf.reverse(label_shape, [True])))
    batch_ind = tf.boolean_mask(batch_array, dense_mask)

    indices = tf.transpose(tf.reshape(tf.concat(0, [batch_ind, label_ind]), [2, -1]))
    shape = [batch_size, tf.reduce_max(label_lengths)]
    vals_sparse = gather_nd(labels, indices, shape)
    
    return tf.SparseTensor(tf.to_int64(indices), vals_sparse, tf.to_int64(label_shape))

# Validate and normalize transcriptions. Returns a cleaned version of the label
# or None if it's invalid.
def validate_label(label):
    # For now we can only handle [a-z ']
    if "(" in label or \
       "<" in label or \
       "[" in label or \
       "]" in label or \
       "&" in label or \
       "*" in label or \
       re.search(r"[0-9]", label) != None:
       return None
    
    label = label.replace("-", "")
    label = label.replace("_", "")
    label = label.replace(".", "")
    label = label.replace(",", "")
    label = label.replace("?", "")
    label = label.strip()
    
    return label
