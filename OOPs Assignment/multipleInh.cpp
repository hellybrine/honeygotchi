#include <iostream>
using namespace std;

// Base classes
class Speakable {
public:
    virtual void speak() {
        cout << "Speaking..." << endl;
    }
};

class Moveable {
public:
    virtual void move() {
        cout << "Moving..." << endl;
    }
};

// Derived class (Multiple Inheritance)
class Z : public Speakable, private Moveable {
public:
    int valueZ;

    Z() {
        valueZ = 0;
    }

    void setZ(int z) {
        valueZ = z;
    }

    using Moveable::move;
};

int main() {
    Z objZ;
    
    int z;
    cout << "Enter value for Z: ";
    cin >> z;
    
    objZ.setZ(z);
    objZ.move();  // Accessing the inherited function

    // objZ.speak(); // This will result in an error because speak is inaccessible due to private inheritance.

    cout << "ValueZ: " << objZ.valueZ << endl;

    return 0;
}
