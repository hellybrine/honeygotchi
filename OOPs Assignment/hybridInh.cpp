#include <iostream>
using namespace std;

// Base class
class X {
public:
    int valueX;

    X() {
        valueX = 0;
    }

    void setX(int x) {
        valueX = x;
    }
};

// Single Inheritance
class Y : public X { // Change private inheritance to public inheritance
public:
    int valueY;

    Y() {
        valueY = 0;
    }

    void setY(int y) {
        valueY = y;
    }
};

// Interface
class Speakable {
public:
    virtual void speak() {
        cout << "Speaking..." << endl;
    }
};

// Derived class (Hybrid Inheritance)
class Z : public Y, public Speakable { // Use public inheritance for Y and Speakable
public:
    int valueZ;

    Z() {
        valueZ = 0;
    }

    void setZ(int z) {
        valueZ = z;
    }
};

int main() {
    Z objZ;

    int x, y, z;
    cout << "Enter value for X: ";
    cin >> x;
    cout << "Enter value for Y: ";
    cin >> y;
    cout << "Enter value for Z: ";
    cin >> z;

    objZ.setY(y);
    objZ.setX(x);  // Accessing the inherited function from X
    objZ.setZ(z);

    objZ.speak();  // Accessing the overridden speak function from Speakable

    cout << "ValueX: " << objZ.valueX << endl;
    cout << "ValueY: " << objZ.valueY << endl;
    cout << "ValueZ: " << objZ.valueZ << endl;

    return 0;
}
