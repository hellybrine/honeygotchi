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

// Intermediate class
class Y : public X {
public:
    int valueY;

    Y() {
        valueY = 0;
    }

    void setY(int y) {
        valueY = y;
    }
};

// Derived class (Multilevel Inheritance)
class Z : public Y {
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
    objZ.setX(x);  // Accessing the inherited function
    objZ.setZ(z);

    cout << "ValueX: " << objZ.valueX << endl;
    cout << "ValueY: " << objZ.valueY << endl;
    cout << "ValueZ: " << objZ.valueZ << endl;

    return 0;
}
