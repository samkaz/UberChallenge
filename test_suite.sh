#! /bin/bash

url=http://127.0.0.1:5000/email
silent="--silent"
post="-X POST"

# Test 1
# A complete request.
response="$(curl $silent $post $url -H "Content-Type: application/json" -d "@test1_payload")"

if ! [[ $(echo $response | grep -m 1 "Request successfully serviced.") ]]; then
    echo "test 1 failed" 
fi

# Test 2
# Missing content-type header.
response="$(curl $silent $post $url -d "@test2_payload")"

# todo put in full message
if ! [[ $(echo $response | grep -m 1 "Failed to load JSON.") ]]; then
    echo "test 2 failed" 
fi

# todo cover all missing fields?

# Test 3
# Missing to_email field.
response="$(curl $silent $post $url -H "Content-Type: application/json" -d "@test3_payload")"

if ! [[ $(echo $response | grep -m 1 "To Email is a required field.") ]]; then
    echo "test 3 failed" 
fi

# Test 4
# Missing from_email field.
response="$(curl $silent $post $url -H "Content-Type: application/json" -d "@test4_payload")"

if ! [[ $(echo $response | grep -m 1 "From Email is a required field.") ]]; then
    echo "test 4 failed" 
fi

# Test 5
# from_email missing @ symbol.
response="$(curl $silent $post $url -H "Content-Type: application/json" -d "@test5_payload")"

if ! [[ $(echo $response | grep -m 1 "Email does not contain @ symbol.") ]]; then
    echo "test 5 failed" 
fi

# Test 6
# to_email is too short.
response="$(curl $silent $post $url -H "Content-Type: application/json" -d "@test6_payload")"

if ! [[ $(echo $response | grep -m 1 "Email length is too short.") ]]; then
    echo "test 6 failed" 
fi

# Test 7
# Missing to_name field.
response="$(curl $silent $post $url -H "Content-Type: application/json" -d "@test7_payload")"

if ! [[ $(echo $response | grep -m 1 "To Name is a required field.") ]]; then
    echo "test 7 failed" 
fi

# Test 8
# Missing from_name field.
response="$(curl $silent $post $url -H "Content-Type: application/json" -d "@test8_payload")"

if ! [[ $(echo $response | grep -m 1 "From Name is a required field.") ]]; then
    echo "test 8 failed" 
fi

# Test 9
# from_name is too short.
response="$(curl $silent $post $url -H "Content-Type: application/json" -d "@test9_payload")"

if ! [[ $(echo $response | grep -m 1 "Name length is too short.") ]]; then
    echo "test 9 failed" 
fi

# Test 10
# Missing subject field.
response="$(curl $silent $post $url -H "Content-Type: application/json" -d "@test10_payload")"

if ! [[ $(echo $response | grep -m 1 "Subject is a required field.") ]]; then
    echo "test 10 failed" 
fi

# Test 11
# subject field is empty.
response="$(curl $silent $post $url -H "Content-Type: application/json" -d "@test11_payload")"

if ! [[ $(echo $response | grep -m 1 "Subject length is too short.") ]]; then
    echo "test 11 failed" 
fi

# Test 12
# Missing body field.
response="$(curl $silent $post $url -H "Content-Type: application/json" -d "@test12_payload")"

if ! [[ $(echo $response | grep -m 1 "Body is a required field.") ]]; then
    echo "test 12 failed" 
fi

# Test 13
# body field is empty.
response="$(curl $silent $post $url -H "Content-Type: application/json" -d "@test13_payload")"

if ! [[ $(echo $response | grep -m 1 "Body length is too short.") ]]; then
    echo "test 13 failed" 
fi
