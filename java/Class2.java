public class Class2 {
	
	//this class just stores one string
	String info;

	public Class2(String info) {//this comment is hard to parse
		this.info = info;
		new Nesty().print_nest();
	}

	public void print_info() {
		System.out.println(this.info);
		System.out.println(" /* not a comment */");
		/* multi-line
		 * comment */
	}

	public class Nesty {
		public void print_nest() {
			System.out.println("I am nested");
		}
	}
}
