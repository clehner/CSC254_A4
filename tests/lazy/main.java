import list.*;


class Program
{
    public static void main(String[] args)
    {
        Cons<String> c = new Cons<String>("Hello",
                                          new Cons<String>(" World", null));

        while (c != null)
        {
            System.out.println(c.Head());
            c = c.Tail();
        }

        LazyCons l = new LazyCons(
            new Thunk<Object>() { public Object invoke() { return "Hello"; } },
            new Thunk<LazyCons>() 
            { 
                public LazyCons invoke() 
                { 
                    return new LazyCons(
                        new Thunk<Object>() 
                            { public Object invoke() { return " World"; } }, null);
                }
            });

        while (l != null)
        {
            System.out.println(l.Head());
            l = l.Tail();
        }


    }
}
