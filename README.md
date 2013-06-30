MReducer
========

A GUI of mencoder to reduce movie file size by xvid encoding

In fact, the main purpose of this project is to demonstrate the yelib, which includes 2 main parts. One is a simple QT wrapper of PySide, one is an event driven task system implemented with Python generator.
To use this program, go to http://www.mplayerhq.hu/design7/dload.html download mplayer and extract mencoder to *bin* directory.

QT wrapper
--------
- yelib.layout 

	- ***yBoxLayout***

		Define a list of rows and each row is a list of widgets. Then add widgets one by one for each row, None means stretched space. If the widget is string or unicode, it will be converted to QLabel automatically.

		This layout is just based on row, the position of widgets affect with each other in the same row, but not in different rows. 

	- ***yGridLayout***

		Define a list of rows and each row is a list of widgets.
		Then add widgets one by one for each row, None means empty widget if it's not at the end of a row. If the widget is string or unicode, it will be converted to QLabel automatically.

		This layout is based on row and column, the position of widgets affect each other. The column count is determined by the maximum widgets of a row. If a widget will occupy more than one column or row, use the form of (widget, rows, columns) instead. yGridLayout always tries to stretch to width of its container. Combine yBoxLayout and yGridLayout together to make the layout as you wish.

	- Examples
		<pre>
		txtInput = QLineEdit()
		btnStart = QPushButton('Start')
		lt = yBoxLayout([
		    [ 'Input', txtInput ],
			[ btnStart, None ],
		])
		self.setLayout(lt)
		</pre>


- yelib.widgets

	- ***FileSelector***(label, title, filter="*.*", type="file")

		Draws 3 widgets: label, text editor and a button. Press the button to open file/directory selecting dialog. The arguments:
		- label: The label in the dialog
		- title: The title of the dialog
		- filter: default is *.* to match all files.
		- type: *file* to select one file (default); *files* to select multiple files; *dir* to select a directory

Task system
--------
- yelib.task

	- TaskOutput: Task function should send out this object for handlers
	- Task: Define task steps(functions) and handler functions for the task begin, end and progress processes.
	- TaskWorker: Start a thread, fetch task from task queue and run task. For each task, there might be multiple steps to go. 
	- TaskHandler: Connect handler function with GUI by QT Signal system
	- CmdTask: Task function for external command
	- Examples
		<pre>
	    def _startConvert(self, row):
	        worker = TaskWorker()
	        def begin():
				self.status.setText('Started ...')
	        def end():
				self.status.setText('Stopped ...')
	        def handler(msg):
				t = msg.type
				o = msg.output
	            if t == OutputType.OUTPUT:
					self.status.setText("progress: " + msg.output)
	            if t == OutputType.NOTIFY and o.startswith('EXIT '):
	                code = int(o.split()[1])
	                if code == 0:
						self.status.setText("done")
	                else:
						self.status.setText("error")
			# ... ...
			# some initialization work
			# ... ...
	        task = Task(CmdTask(["ls", "/tmp"]))
	        task.init(
	        	TaskHandler(begin), TaskHandler(end), TaskHandler(handler)
	            )
	        worker.add_task(task)
		</pre>

To be improved
--------
- Better interface to wrap mencoder options
- Lack of exception handler

