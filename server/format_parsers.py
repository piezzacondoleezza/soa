import timeit
import json
from dicttoxml import dicttoxml
import data_pb2
import yaml
import msgpack
import sys
import pickle
from xml_marshaller import xml_marshaller
import jsonpickle
from abc import abstractmethod, ABC


data_template = {
    "string": "cuttyyy",
    "array" : [6, 3, 3, 5, 0, 5, 4, 1],
    "dict": {
        'lemongrass': 173,
        'assembly': -228,
        'genesis': 73
    },
    "int_num": 228,
    "float_num": 3.14159
}

from dataclasses_avroschema import AvroModel


class AvroData(AvroModel):
    string = "cuttyyy"
    array = [6, 3, 3, 5, 0, 5, 4, 1]
    dict = {
        'lemongrass': 173,
        'assembly': -228,
        'genesis': 73
    }
    int_num = 228
    float_num = 3.14159


class Base(ABC):
    @abstractmethod
    def serialize(self, data):
        return None

    @abstractmethod
    def deserialize(self, data):
        return None


class NativeFormat(Base):
    def serialize(self, data):
        return pickle.dumps(data)
    def deserialize(self, data):
        return pickle.loads(data)

class XmlFormat(Base):
    def serialize(self, data):
        return xml_marshaller.dumps(data)
    def deserialize(self, data):
        return xml_marshaller.loads(data)

class JsonFormat(Base):
    def serialize(self, data):
        return jsonpickle.encode(data)
    def deserialize(self, data):
        return jsonpickle.decode(data)

class YamlFormat(Base):
    def serialize(self, data):
        return yaml.dump(data)
    def deserialize(self, data):
        return yaml.load(data, yaml.FullLoader)

class MessagePackFormat(Base):
    def serialize(self, data):
        return msgpack.packb(data, use_bin_type=True)
    def deserialize(self, data):
        return msgpack.unpackb(data, raw=False)

class ProtobufFormat(Base):
    def serialize(self, data):
        return data.SerializeToString()
    def deserialize(self, data):
        msg = data_pb2.Data()
        return msg.ParseFromString(data)

class AvroFormat(Base):
    def serialize(self, data):
        return data.serialize()
    def deserialize(self, data):
        x = AvroData()
        return x.deserialize(data)


def timer_func(format_class, data_, size_of_data):
    ser_data_size = size_of_data
    serialization_time = timeit.timeit(lambda: format_class.serialize(data_), number=500)
    ser_data = format_class.serialize(data_)
    deserialization_time = timeit.timeit(lambda: format_class.deserialize(ser_data), number=500)
    return (serialization_time * 1000.0, deserialization_time * 1000.0, ser_data_size)


def native_format():
    format_class = NativeFormat()    
    return timer_func(format_class, data_template, sys.getsizeof(data_template))

def xml_format():
    format_class = XmlFormat()
    return timer_func(format_class, data_template, sys.getsizeof(dicttoxml(data_template)))

def json_format():
    format_class = JsonFormat()
    return timer_func(format_class, data_template, sys.getsizeof(json.dumps(data_template)))

def yaml_format():
    format_class = YamlFormat()
    return timer_func(format_class, data_template, sys.getsizeof(yaml.dump(data_template)))

def msg_pack_format():
    format_class = MessagePackFormat()
    return timer_func(format_class, data_template, sys.getsizeof(msgpack.packb(data_template, use_bin_type=True)))

def proto_format():
    msg = data_pb2.Data()
    msg.string = data_template["string"]
    msg.int_num = data_template["int_num"]
    msg.float_num = data_template["float_num"]
    for value in data_template["array"]:
        msg.array.append(value)
    for key, value in data_template["dict"].items():
        msg.dict[key] = value
    format_class = ProtobufFormat()
    return timer_func(format_class, msg, sys.getsizeof(msg.SerializeToString()))

def avro_format():
    format_class = AvroFormat()
    return timer_func(format_class, AvroData(), sys.getsizeof(AvroData().serialize()))


if __name__ == "__main__":
    print(avro_format())
    print(proto_format())
    print(msg_pack_format())
    print(yaml_format())
    print(json_format())
    print(native_format())
    print(xml_format())