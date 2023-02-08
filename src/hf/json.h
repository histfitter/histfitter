/**
Copyright 2010-2015 Bernard van Gastel, bvgastel@bitpowder.com.
This file is standalone and not part of any release.

Bit Powder Libraries is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Bit Powder Libraries is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Bit Powder Libraries.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef JSON_H
#define JSON_H

#include <functional>
#include <iterator>
#include <map>
#include <vector>
#include <string>
#include <ostream>
#include <iostream>
#include <exception>

class JSONException : public std::exception {
    const char* reason;
public:
    JSONException(const char* reason) : reason(reason) {
    }
    const char* what() const throw() override {
        return reason;
    }
};

class JSON {
  public:
    template <class OtherArray>
    JSON(const std::vector<OtherArray>& otherArray) : JSON(Array()) {
        for (const auto& v : otherArray)
            array.push_back(JSON(v));
    }
    template <class OtherObject>
    JSON(const std::map<std::string, OtherObject>& otherObject) : JSON(Object()) {
        for (const auto& v : otherObject)
            object.insert(std::make_pair(v.first, JSON(v.second)));
    }

    static std::map<std::string, JSON> Object() {
        return {};
    }
    static std::vector<JSON> Array() {
        return {};
    }
  private:
    enum {JSONNull, JSONBool, JSONString, JSONLongNumber, JSONNumber, JSONArray, JSONObject} type;
    union {
        bool b;
        std::string str;
        double number;
        std::vector<JSON> array;
        std::map<std::string, JSON> object;
    };
  public:
    JSON() : type(JSONNull) {
    }
    explicit JSON(bool b) : type(JSONBool), b(b) {
    }
    
    // constructor for numeric types
    // Note GJ: this effectively evaluates to e.g. int JSON(int, int* enabler=nullptr), the boolean constructor is not defined but used from above
    template <class NumericType>
    JSON(NumericType number, typename std::enable_if<!std::is_same<bool,NumericType>::value and std::is_arithmetic<NumericType>::value,NumericType>::type* enabler = nullptr) : 
        type(JSONNumber), number(number) {
    } 
    
    JSON(const std::string& str) : type(JSONString), str(str) {
    }
    JSON(const char* str) : type(JSONString), str(str) {
    }
    JSON(const std::vector<JSON>& array) : type(JSONArray), array(array) {
    }
    JSON(std::vector<JSON>&& array) : type(JSONArray), array(std::move(array)) {
    }
    JSON(const std::map<std::string, JSON>& object) : type(JSONObject), object(object) {
    }
    JSON(std::map<std::string, JSON>&& object) : type(JSONObject), object(std::move(object)) {
    }
    ~JSON() {
        clear();
    }
    void clear();

    JSON(JSON&& b);
    JSON(const JSON& other);
    JSON& operator=(JSON &&b);
    JSON& operator=(const JSON& b);
    bool operator==(const JSON& b) const;

    bool isVector() const {
        return type == JSONArray;
    }

    bool isObject() const {
        return type == JSONObject;
    }

    bool isString() const {
        return type == JSONString;
    }
    
    bool isLongNumber() const {
        return type == JSONLongNumber;
    }

    bool isNumber() const {
        return type == JSONNumber;
    }

    bool isBool() const {
        return type == JSONBool;
    }

    bool isNull() const {
        return type == JSONNull;
    }

    const std::vector<JSON>& asVector() const {
        if (!isVector())
            throw JSONException("not an array");
        return array;
    }

    std::vector<JSON>& asVector() {
        if (!isVector())
            throw JSONException("not an array");
        return array;
    }

    const std::map<std::string, JSON>& asObject() const {
        if (!isObject())
            throw JSONException("not an object");
        return object;
    }

    std::map<std::string, JSON>& asObject() {
        if (!isObject())
            throw JSONException("not an object");
        return object;
    }

    const std::string& asString() const {
        if (!isString())
            throw JSONException("not a string");
        return str;
    }

    std::string& asString() {
        if (!isString())
            throw JSONException("not a string");
        return str;
    }

    double asNumber() const {
        if (!isNumber())
            throw JSONException("not a number");
        return number;
    }

    bool asBool() const {
        if (!isBool())
            throw JSONException("not a boolean");
        return b;
    }

    operator std::vector<JSON>& () {
        return asVector();
    }

    operator std::map<std::string, JSON>& () {
        return asObject();
    }

    operator std::string() {
        return asString();
    }

    explicit operator double() {
        return asNumber();
    }

    explicit operator bool() {
        return asBool();
    }

    virtual void print(std::ostream& out) const;

    JSON& operator[](const std::string& lookup) {
        return asObject()[lookup];
    }
    JSON& operator[](int lookup) {
        return asVector()[lookup];
    }

    class iterator {
        friend class JSON;
        std::vector<JSON>* contents;
        unsigned long index;
        iterator(std::vector<JSON>* contents, unsigned long index) : contents(contents), index(index) {
        }
      public:
        bool operator==(const iterator& it) const {
            return contents == it.contents && index == it.index;
        }
        bool operator!=(const iterator& it) const {
            return !(*this == it);
        }
        JSON& operator*() const {
            return (*contents)[index];
        }
        iterator& operator++() {
            index++;
            return *this;
        }
    };
    iterator begin();
    iterator end();
};

typedef std::string Key;

typedef std::string StringT;
typedef std::vector<JSON> ArrayT;
typedef std::map<Key, JSON> ObjectT;
typedef double NumberT;

#endif
