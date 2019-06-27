//
//	md2.cpp - source file
//
//	David Henry - tfc_duke@hotmail.com
//
#include <iostream>
#include <sstream>

#include	<GL/glut.h>
#include	<fstream>

#include	"md2.h"
//#include	"texture.h"




//static float	*shadedots = CMD2Model::anorms_dots[0];
static vec3_t	lcolor;


/////////////////////////////////////////////////

vec3_t			g_lightcolor	= { 1.0, 1.0, 1.0 };
int				g_ambientlight	= 32;
float			g_shadelight	= 128;
float			g_angle			= 0.0;

/////////////////////////////////////////////////



// ----------------------------------------------
// constructor - reset all data.
// ----------------------------------------------

CMD2Model::CMD2Model( void )
{
	m_vertices		= 0;
	m_glcmds		= 0;
	m_lightnormals	= 0;

	num_frames		= 0;
	num_xyz			= 0;
	num_glcmds		= 0;

	m_texid			= 0;
	m_scale			= 1.0;

	//SetAnim( 0 );
}



// ----------------------------------------------
// destructeur - free allocated memory.
// ----------------------------------------------

CMD2Model::~CMD2Model( void )
{
	delete [] m_vertices;
	delete [] m_glcmds;
	delete [] m_lightnormals;
}



// ----------------------------------------------
// LoadModel() - load model from file.
// ----------------------------------------------

bool CMD2Model::LoadModel( const char *filename )
{
	std::ifstream	file;			// file stream
	md2_t			header;			// md2 header
	char			*buffer;		// buffer storing frame data
	frame_t			*frame;			// temporary variable
	vec3_t			*ptrverts;		// pointer on m_vertices
	int				*ptrnormals;	// pointer on m_lightnormals


	// try to open filename
	file.open( filename, std::ios::in | std::ios::binary );

	if( file.fail() )
		return false;

	// read header file
	file.read( (char *)&header, sizeof( md2_t ) );


	/////////////////////////////////////////////
	//		verify that this is a MD2 file

	// check for the ident and the version number

	if( (header.ident != MD2_IDENT) && (header.version != MD2_VERSION) )
	{
		// this is not a MD2 model
		file.close();
		return false;
	}

	/////////////////////////////////////////////


	// initialize member variables
	num_frames	= header.num_frames;
	num_xyz		= header.num_xyz;
	num_glcmds	= header.num_glcmds;

	

	// allocate memory
	m_vertices		= new vec3_t[ num_xyz * num_frames ];
	m_glcmds		= new int[ num_glcmds ];
	m_lightnormals	= new int[ num_xyz * num_frames ];
	buffer			= new char[ num_frames * header.framesize ];


	/////////////////////////////////////////////
	//			reading file data

	// read frame data...
	file.seekg( header.ofs_frames, std::ios::beg );
	file.read( (char *)buffer, num_frames * header.framesize );
	
	//std::cout << header.framesize << std::endl;

	// read opengl commands...
	file.seekg( header.ofs_glcmds, std::ios::beg );
	file.read( (char *)m_glcmds, num_glcmds * sizeof( int ) );

	/////////////////////////////////////////////

	frame_t *test = (frame_t *)&buffer[ header.framesize * 0 ];
	std::cout << test->scale[2] << std::endl;

	// vertex array initialization
	for( int j = 0; j < num_frames; j++ )
	{
		// ajust pointers
		frame		= (frame_t *)&buffer[ header.framesize * j ];
		ptrverts	= &m_vertices[ num_xyz * j ];
		ptrnormals	= &m_lightnormals[ num_xyz * j ];

		for( int i = 0; i < num_xyz; i++ )
		{
			ptrverts[i][0] = (frame->verts[i].v[0] * frame->scale[0]) + frame->translate[0];
			ptrverts[i][1] = (frame->verts[i].v[1] * frame->scale[1]) + frame->translate[1];
			ptrverts[i][2] = (frame->verts[i].v[2] * frame->scale[2]) + frame->translate[2];

			ptrnormals[i] = frame->verts[i].lightnormalindex;
		}
	}


	// free buffer's memory
	delete [] buffer;

	// close the file and return
	file.close();
	return true;
}