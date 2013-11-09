public class List{

	Node head;
	
	public void add(Node n){
		n.setNext(head);
		head = n;
	}
	
	public void add2(Node n){
		Node current = head;
		while (current.getNext() != null){
			current = current.getNext();
		}
		
		current.setNext(n);
	}
		
	public void delete(int n){
		Node current = head;
		while (current.getNext() != null && current.getNext().getData() != n){
			current = current.getNext();
		}
		
		if (current.getNext().getData() == n){
			current.setNext( current.getNext().getNext() );
		} else {
			return;
		}
	}
	
	public boolean lookup(int n){
		Node current = head;
		while (current.getNext() != null && current.getNext().getData() != n){
			current = current.getNext();
		}
		
		if (current.getNext().getData() == n){
			return true;
		} else {
			return false;
		}
	}
	
	public static void main(String[] args){
		List l = new List();
		
		l.add(new Node(5));
		l.add(new Node(7));
		l.add(new Node(3));
		l.add(new Node(10));
		
	}

    static class Node{

    	private int data;
    	private Node next;
    	
    	public Node(int n){
    		this.data = n;
    	}
	

    	public void setNext(Node n){
    		this.next = n;
    	}
	
    	public Node getNext(){
    		return this.next;
       	}
	
    	public int getData(){
    		return data;
    	}
    }
}
