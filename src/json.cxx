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

#include <functional>
#include <iterator>
#include <map>
#include <vector>
#include <string>
#include <ostream>
#include <iostream>
#include <iomanip>
#include <cmath>

#include "json.h"

template <class T>
inline void destroy(T* object) {
    object->~T();
}

void JSON::clear() {
    if (type == JSONString)
        destroy(&str);
    else if (type == JSONArray) {
        destroy(&array);
    } else if (type == JSONObject)
        destroy(&object);
    type = JSONNull;
}

JSON& JSON::operator=(const JSON& other) {
    if (this == &other)
        return *this;
    clear();
    type = other.type;
    if (type == JSONBool)
        b = other.b;
    else if (type == JSONString)
        new (&str) StringT(other.str);
    else if (type == JSONNumber or type == JSONLongNumber)
        number = other.number;
    else if (type == JSONArray)
        new (&array) ArrayT(other.array);
    else if (type == JSONObject)
        new (&object) ObjectT(other.object);
    return *this;
}

bool JSON::operator==(const JSON& other) const {
    if (type == other.type) {
        if (type == JSONNull)
            return true;
        if (type == JSONBool)
            return b == other.b;
        if (type == JSONString)
            return str == other.str;
        if (type == JSONNumber or type == JSONLongNumber)
            return number == other.number;
        if (type == JSONArray)
            return array == other.array;
        if (type == JSONObject)
            return object == other.object;
    }
    return false;
}

JSON& JSON::operator=(JSON &&other) {
    clear();
    type = other.type;
    if (type == JSONBool)
        b = other.b;
    else if (type == JSONString)
        new (&str) StringT(std::move(other.str));
    else if (type == JSONNumber or type == JSONLongNumber)
        number = other.number;
    else if (type == JSONArray)
        new (&array) ArrayT(std::move(other.array));
    else if (type == JSONObject)
        new (&object) ObjectT(std::move(other.object));
    return *this;
}

JSON::JSON(const JSON& other) :
type(other.type) {
    if (type == JSONBool)
        b = other.b;
    else if (type == JSONString)
        new (&str) StringT(other.str);
    else if (type == JSONNumber or type == JSONLongNumber)
        number = other.number;
    else if (type == JSONArray)
        new (&array) ArrayT(other.array);
    else if (type == JSONObject)
        new (&object) ObjectT(other.object);
}

JSON::JSON(JSON &&other) :
type(other.type) {
    if (type == JSONBool)
        b = other.b;
    else if (type == JSONString)
        new (&str) StringT(std::move(other.str));
    else if (type == JSONNumber or type == JSONLongNumber)
        number = other.number;
    else if (type == JSONArray)
        new (&array) ArrayT(std::move(other.array));
    else if (type == JSONObject)
        new (&object) ObjectT(std::move(other.object));
}

void JSON::print(std::ostream& out) const {
    if (type == JSONNull)
        out << "null";
    if (type == JSONBool)
        out << (b ? "true" : "false");
    if (type == JSONLongNumber)
        out << std::fixed << number;
    
    if (type == JSONNumber and !(std::isinf(number) or std::isnan(number))) {
        out << std::scientific << std::setprecision(6) << number;
    } else if (type == JSONNumber) {
        out << '"' << number << '"';
    }
    
    if (type == JSONString)
        out << '"' << str << '"';
    if (type == JSONArray) {
        out << "[";
        bool first = true;
        for (auto& it : array) {
            if (!first)
                out << ",";
            it.print(out);
            first = false;
        }
        out << "]";
    }
    if (type == JSONObject) {
        out << "{";
        bool first = true;
        for (auto& it : object) {
            if (!first)
                out << ",";
            out << "\"" << it.first << "\":";
            it.second.print(out);
            first = false;
        }
        out << "}";
    }
}

JSON::iterator JSON::begin() {
    return {isVector() ? &array : nullptr, 0};
}

JSON::iterator JSON::end() {
    return isVector() ? iterator(&array, array.size()) : iterator(nullptr, 0);
}

namespace std {
inline std::ostream& operator<< (std::ostream& out, const JSON& json) {
    json.print(out);
    return out;
}
}

