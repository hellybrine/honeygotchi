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

                                // Derived class (Single Inheritance)
class Y : public X {            // Change private inheritance to public inheritance
public:
    int valueY;

    Y() {
        valueY = 0;
    }

    void setY(int y) {
        valueY = y;
    }
};

int main() {
    Y objY;

    int x, y;
    cout << "Enter value for X: ";
    cin >> x;
    cout << "Enter value for Y: ";
    cin >> y;

    objY.setY(y);
    objY.setX(x);                                       // Accessing the inherited function is allowed

    cout << "ValueX: " << objY.valueX << endl;          // Access valueX directly
    cout << "ValueY: " << objY.valueY << endl;

    return 0;
}
