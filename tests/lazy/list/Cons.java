package list;

public class Cons<T>
{
    private T head;
    private Cons<T> tail;

    public T Head()
    {
        return head;
    }

    public Cons<T> Tail()
    {
        return tail;
    }

    public Cons(T head, Cons<T> tail)
    {
        this.head = head;
        this.tail = tail;
    }
}
