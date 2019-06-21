# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

# """Tests for RecordWriter"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import six
import os
from tensorboard.summary.writer.record_writer import RecordWriter
from tensorboard.compat.tensorflow_stub import errors
from tensorboard.compat.tensorflow_stub.pywrap_tensorflow import PyRecordReader_New
from tensorboard import test as tb_test


class RecordWriterTest(tb_test.TestCase):

  def test_expect_bytes_written(self):
    filename = os.path.join(self.get_temp_dir(), "expect_bytes_written")
    byte_len = 64
    w = RecordWriter(open(filename, 'wb'))
    bytes_to_write = b"x" * byte_len
    w.write(bytes_to_write)
    w.close()
    with open(filename, 'rb') as f:
      self.assertEqual(len(f.read()), (8 + 4 + byte_len + 4))  # uint64+uint32+data+uint32

  def test_empty_record(self):
    filename = os.path.join(self.get_temp_dir(), "empty_record")
    w = RecordWriter(open(filename, 'wb'))
    bytes_to_write = b""
    w.write(bytes_to_write)
    w.close()
    r = PyRecordReader_New(filename)
    r.GetNext()
    self.assertEqual(r.record(), bytes_to_write)

  def test_record_writer_roundtrip(self):
    filename = os.path.join(self.get_temp_dir(), "record_writer_roundtrip")
    w = RecordWriter(open(filename, 'wb'))
    chunks_to_write = ["hello world{}".format(i).encode() for i in range(10)]
    for bytes in chunks_to_write:
      w.write(bytes)
    w.close()

    r = PyRecordReader_New(filename)
    for bytes in chunks_to_write:
      r.GetNext()
      self.assertEqual(r.record(), bytes)

  def test_record_immediate_read(self):
    filename = os.path.join(self.get_temp_dir(), "record_immediate_read")
    chunks_to_write = ["hello world{}".format(i).encode() for i in range(10)]
    w = RecordWriter(open(filename, 'wb'))
    r = PyRecordReader_New(filename)
    with self.assertRaises(errors.OutOfRangeError):
      r.GetNext()
    for bytes in chunks_to_write:
      w.write(bytes)
      w.flush()
      r.GetNext()
      self.assertEqual(r.record(), bytes)
    w.close()

  def test_expect_bytes_written_bytes_IO(self):
    byte_len = 64
    Bytes_io = six.BytesIO()
    w = RecordWriter(Bytes_io)
    bytes_to_write = b"x" * byte_len
    w.write(bytes_to_write)
    self.assertEqual(len(Bytes_io.getvalue()), (8 + 4 + byte_len + 4))  # uint64+uint32+data+uint32


if __name__ == '__main__':
  tb_test.main()
