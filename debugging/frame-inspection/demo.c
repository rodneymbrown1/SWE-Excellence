/* Practice target: a few nested calls with scalars, a struct, a pointer, and an array. */
#include <stdio.h>
#include <string.h>

typedef struct {
    char name[16];
    int  qty;
    double unit_price;
} Item;

typedef struct {
    Item  items[3];
    int   count;
    double total;
} Order;

static double apply_discount(double subtotal, int qty)
{
    double rate = qty >= 10 ? 0.10 : 0.0;
    return subtotal * (1.0 - rate);
}

static double line_total(const Item *it)
{
    double sub = it->qty * it->unit_price;
    return apply_discount(sub, it->qty);
}

static void compute_total(Order *o)
{
    o->total = 0;
    for (int i = 0; i < o->count; i++)
        o->total += line_total(&o->items[i]);
}

static void add_item(Order *o, const char *name, int qty, double price)
{
    Item *it = &o->items[o->count++];
    strncpy(it->name, name, sizeof it->name - 1);
    it->qty = qty;
    it->unit_price = price;
}

int main(void)
{
    Order order = {0};
    add_item(&order, "widget", 12, 2.50);
    add_item(&order, "gadget", 3, 10.00);
    compute_total(&order);
    printf("total = %.2f\n", order.total);
    return 0;
}
