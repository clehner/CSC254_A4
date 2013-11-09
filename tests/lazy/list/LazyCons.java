package list;

import list.Thunk;

public class LazyCons
{
    private Thunk<Object> head;
    private Thunk<LazyCons> tail;

    public LazyCons(Thunk<Object> head, Thunk<LazyCons> tail)
    {
        this.head = head;
        this.tail = tail;
    }

    public Object Head()
    {
        return head.invoke();
    }

    public LazyCons Tail()
    {
        if (tail == null)
            return null;
        return tail.invoke();
    }
}